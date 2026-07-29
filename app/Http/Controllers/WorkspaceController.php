<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class WorkspaceController extends Controller
{
  public function store(Request $request)
{
    // Validate the incoming request
    $validated = $request->validate([
        'name' => 'required|string|max:255',
        'description' => 'nullable|string',
    ]);

    // Create a workspace for the authenticated user
    $workspace = $request->user()->workspaces()->create([
        'name' => $validated['name'],
        'description' => $validated['description'],
    ]);

    // Return the created workspace
    return response()->json([
        'message' => 'Workspace created successfully.',
        'workspace' => $workspace,
    ], 201);
}

public function index(Request $request){
    $workspaces = $request->user()->workspaces;
    return response()->json($workspaces);
}

public function show(Request $request, $id){
    $workspace = $request->user()->workspaces()->findOrFail($id);
    return response()->json($workspace);
}

public function update(Request $request, $id){
    $validated = $request->validate([
        'name' => 'required|string|max:255',
        'description' => 'nullable|string',
    ]);

    $workspace = $request->user()->workspaces()->findOrFail($id);
    $workspace->update($validated);

    return response()->json([
        'message' => 'Workspace updated successfully.',
        'workspace' => $workspace,
    ]);

}

public function destroy(Request $request, $id){
    $workspace = $request->user()->workspaces()->findOrFail($id);
    $workspace->delete();

    return response()->json([
        'message'=>'workspace deleted successfully.',
    ]);
}

}
