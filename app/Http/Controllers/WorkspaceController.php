<?php

namespace App\Http\Controllers;

use App\Http\Requests\ShareWorkspaceRequest;
use App\Http\Requests\StoreWorkspaceRequest;
use App\Models\User;
use App\Models\Workspace;
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

        $workspace->setAttribute('role', 'owner');
        $workspace->setAttribute('is_owner', true);

        return response()->json([
            'message' => 'Workspace created successfully.',
            'workspace' => $workspace,
        ], 201);
    }

    public function index(Request $request)
    {
        $owned = $request->user()->workspaces->map(function (Workspace $workspace) {
            $workspace->setAttribute('role', 'owner');
            $workspace->setAttribute('is_owner', true);
            return $workspace;
        });

        $shared = $request->user()->sharedWorkspaces->map(function (Workspace $workspace) {
            $workspace->setAttribute('role', $workspace->pivot->role);
            $workspace->setAttribute('is_owner', false);
            return $workspace;
        });

        return response()->json($owned->concat($shared)->values());
    }

    public function show(Request $request, $id)
    {
        $workspace = $request->user()->findAccessibleWorkspace($id);

        if (!$workspace) {
            abort(404);
        }

        return response()->json($workspace);
    }

    public function update(StoreWorkspaceRequest $request, $id)
    {
        $validated = $request->validated();

        $workspace = $request->user()
            ->workspaces()
            ->findOrFail($id);

        $workspace->update($validated);

        $workspace->setAttribute('role', 'owner');
        $workspace->setAttribute('is_owner', true);

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

    public function share(ShareWorkspaceRequest $request, Workspace $workspace)
    {
        if ($workspace->user_id !== auth()->id()) {
            abort(403, 'You are not allowed to share this workspace.');
        }

        $user = User::where('email', $request->email)->firstOrFail();

        if ($user->id === auth()->id()) {
            return response()->json([
                'message' => 'You already own this workspace.',
            ], 422);
        }

        $workspace->users()->syncWithoutDetaching([
            $user->id => [
                'role' => $request->role,
            ],
        ]);

        return response()->json([
            'message' => 'Workspace shared successfully.',
            'user' => $user,
            'role' => $request->role,
        ]);
    }

    public function sharedUsers(Request $request, Workspace $workspace)
{
    // Only the workspace owner can see the shared users
    if ($workspace->user_id !== $request->user()->id) {
        abort(403, 'You are not allowed to view shared users.');
    }

    $users = $workspace->users()
        ->where('users.id', '!=', $workspace->user_id)
        ->get()
        ->map(function (User $user) {
            return [
                'id' => $user->id,
                'name' => $user->name,
                'email' => $user->email,
                'role' => $user->pivot->role,
            ];
        });

    return response()->json($users);
}

public function removeSharedUser(
    Request $request,
    Workspace $workspace,
    User $user
) {
    // Only the workspace owner can remove users
    if ($workspace->user_id !== $request->user()->id) {
        abort(403, 'You are not allowed to remove users from this workspace.');
    }

    // Owner cannot be removed
    if ($user->id === $workspace->user_id) {
        return response()->json([
            'message' => 'The workspace owner cannot be removed.',
        ], 422);
    }

    // Check that this user is actually shared with the workspace
    $isShared = $workspace->users()
        ->where('users.id', $user->id)
        ->exists();

    if (!$isShared) {
        return response()->json([
            'message' => 'This user does not have access to this workspace.',
        ], 404);
    }

    $workspace->users()->detach($user->id);

    return response()->json([
        'message' => 'User removed from workspace successfully.',
    ]);
}
}
