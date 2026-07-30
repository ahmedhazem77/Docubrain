<?php

namespace App\Http\Controllers;

use App\Http\Requests\StoreWorkspaceRequest;
use Illuminate\Http\Request;

class WorkspaceController extends Controller
{
    public function store(StoreWorkspaceRequest $request)
    {
        $validated = $request->validated();

        $workspace = $request->user()->workspaces()->create([
            'name' => $validated['name'],
            'description' => $validated['description'],
        ]);

        return response()->json([
            'message' => 'Workspace created successfully.',
            'workspace' => $workspace,
        ], 201);
    }

    public function index(Request $request)
    {
        $workspaces = $request->user()->workspaces;

        return response()->json($workspaces);
    }

    public function show(Request $request, $id)
    {
        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($id);

        return response()->json($workspace);
    }

    public function update(StoreWorkspaceRequest $request, $id)
    {
        $validated = $request->validated();

        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($id);

        $workspace->update($validated);

        return response()->json([
            'message' => 'Workspace updated successfully.',
            'workspace' => $workspace,
        ]);
    }

    public function destroy(Request $request, $id)
    {
        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($id);

        $workspace->delete();

        return response()->json([
            'message' => 'Workspace deleted successfully.',
        ]);
    }
}