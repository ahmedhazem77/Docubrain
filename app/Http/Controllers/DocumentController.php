<?php

namespace App\Http\Controllers;

use App\Http\Requests\UploadDocumentRequest;
use App\Models\Document;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;
use App\Jobs\ProcessDocumentJob;

class DocumentController extends Controller
{
    public function store(UploadDocumentRequest $request, $workspaceId)
    {
        
        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($workspaceId);

        
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
        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($workspaceId);

        $documents = $workspace->documents;

        return response()->json($documents);
    }

    public function show(Request $request, $documentId)
    {
        $document = Document::findOrFail($documentId);

        if ($document->workspace->user_id !== $request->user()->id) {
            abort(403);
        }

        return response()->json($document);
    }

    public function destroy(Request $request, $documentId)
    {
        $document = Document::findOrFail($documentId);

        if ($document->workspace->user_id !== $request->user()->id) {
            abort(403);
        }

        Storage::delete($document->file_path);

        $document->delete();

        return response()->json([
            'message' => 'Document deleted successfully.',
        ]);
    }

}