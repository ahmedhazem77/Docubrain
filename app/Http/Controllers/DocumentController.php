<?php

namespace App\Http\Controllers;

use App\Http\Requests\UploadDocumentRequest;
use App\Jobs\ProcessDocumentJob;
use App\Models\Document;
use App\Models\Workspace;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class DocumentController extends Controller
{
    public function store(UploadDocumentRequest $request, $workspaceId)
    {
        $workspace = $this->findEditableWorkspace($request, $workspaceId);

        $file = $request->file('file');
        $path = $file->store('documents');

        $document = $workspace->documents()->create([
            'file_name' => $file->getClientOriginalName(),
            'file_path' => $path,
            'status' => 'pending',
            'metadata' => [],
        ]);

        ProcessDocumentJob::dispatch($document);

        return response()->json([
            'message' => 'Document uploaded successfully.',
            'document' => $document,
        ], 201);
    }

    public function index(Request $request, $workspaceId)
    {
        $workspace = $this->findReadableWorkspace($request, $workspaceId);

        return response()->json($workspace->documents);
    }

    public function show(Request $request, $documentId)
    {
        $document = Document::findOrFail($documentId);
        $this->assertCanReadWorkspace($request, $document->workspace);

        return response()->json($document);
    }

    public function destroy(Request $request, $documentId)
    {
        $document = Document::findOrFail($documentId);
        $this->assertCanEditWorkspace($request, $document->workspace);

        Storage::delete($document->file_path);
        $document->delete();

        return response()->json([
            'message' => 'Document deleted successfully.',
        ]);
    }

    public function view(Document $document)
    {
        $this->assertCanReadWorkspace(request(), $document->workspace);

        if (!Storage::exists($document->file_path)) {
            abort(404, 'File not found.');
        }

        return Storage::response($document->file_path);
    }

    public function summarize(Request $request, $documentId)
    {
        $document = Document::findOrFail($documentId);
        $this->assertCanReadWorkspace($request, $document->workspace);

        if ($document->status !== 'processed') {
            return response()->json([
                'message' => 'Document must be processed before it can be summarized.',
            ], 422);
        }

        $response = Http::timeout(300)
            ->post(rtrim(config('services.ai_engine.url'), '/')."/documents/{$document->id}/summarize");

        if ($response->failed()) {
            return response()->json([
                'message' => 'Summarization failed.',
            ], 502);
        }

        return response()->json($response->json());
    }

    private function findReadableWorkspace(Request $request, $workspaceId): Workspace
    {
        $workspace = $request->user()->findAccessibleWorkspace($workspaceId);

        if (!$workspace) {
            abort(404);
        }

        return $workspace;
    }

    private function findEditableWorkspace(Request $request, $workspaceId): Workspace
    {
        $workspace = $this->findReadableWorkspace($request, $workspaceId);
        $this->assertCanEditWorkspace($request, $workspace);

        return $workspace;
    }

    private function assertCanReadWorkspace(Request $request, Workspace $workspace): void
    {
        $user = $request->user();

        if ((int) $workspace->user_id === (int) $user->id) {
            return;
        }

        if ($workspace->users()->where('user_id', $user->id)->exists()) {
            return;
        }

        abort(403, 'Unauthorized.');
    }

    private function assertCanEditWorkspace(Request $request, Workspace $workspace): void
    {
        $user = $request->user();

        if ((int) $workspace->user_id === (int) $user->id) {
            return;
        }

        $isEditor = $workspace->users()
            ->where('user_id', $user->id)
            ->wherePivot('role', 'editor')
            ->exists();

        if ($isEditor) {
            return;
        }

        abort(403, 'Unauthorized.');
    }
}
