<?php

namespace App\Http\Controllers;

use App\Models\Conversation;
use Illuminate\Http\Request;

class ConversationController extends Controller
{
    public function store(Request $request)
    {
        $request->validate([
            'workspace_id' => 'required|exists:workspaces,id',
            'title' => 'nullable|string|max:255',
        ]);

        $conversation = Conversation::create([
            'workspace_id' => $request->workspace_id,
            'user_id' => $request->user()->id,
            'title' => $request->title ?? 'New Conversation',
        ]);

        return response()->json($conversation, 201);
    }

    public function index(Request $request, $workspaceId)
    {
        $conversations = Conversation::where('workspace_id', $workspaceId)
            ->where('user_id', $request->user()->id)
            ->latest()
            ->get();

        return response()->json($conversations);
    }

    public function show(Request $request, $conversationId)
    {
        $conversation = Conversation::where('id', $conversationId)
            ->where('user_id', $request->user()->id)
            ->firstOrFail();

        $messages = $conversation->messages()
            ->orderByDesc('id')
            ->limit(20)
            ->get()
            ->sortBy('id')
            ->values();

        $conversation->setRelation('messages', $messages);

        return response()->json($conversation);
    }

    public function storeMessage(Request $request, $conversationId)
    {
        $conversation = Conversation::where('id', $conversationId)
            ->where('user_id', $request->user()->id)
            ->firstOrFail();

        $validated = $request->validate([
            'role' => 'required|in:user,assistant',
            'content' => 'required|string',
            'citations' => 'nullable|array',
        ]);

        $message = $conversation->messages()->create([
            'role' => $validated['role'],
            'content' => $validated['content'],
            'citations' => $validated['citations'] ?? [],
        ]);

        return response()->json($message, 201);
    }

    public function destroy(Request $request, $conversationId)
    {
        $conversation = Conversation::where('id', $conversationId)
            ->where('user_id', $request->user()->id)
            ->firstOrFail();

        $conversation->delete();

        return response()->json([
            'message' => 'Conversation deleted successfully.'
        ]);
    }
}