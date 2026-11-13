<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\WorkspaceController;
use App\Http\Controllers\DocumentController;
use App\Http\Controllers\ConversationController;

use Illuminate\Support\Facades\DB;


Route::get('/test-db', function () {
    return [
        'loaded_extensions' => get_loaded_extensions(),
        'pdo_drivers' => PDO::getAvailableDrivers(),
        'php_binary' => PHP_BINARY,
        'loaded_ini' => php_ini_loaded_file(),
    ];
});

Route::post('/register', [AuthController::class, 'register']);
Route::post('/login', [AuthController::class, 'login']);

Route::middleware('auth:sanctum')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout']);
    Route::post('/workspaces', [WorkspaceController::class, 'store']);
    Route::get('/workspaces', [WorkspaceController::class, 'index']);
    Route::get('/workspaces/{id}', [WorkspaceController::class, 'show']);
    Route::put('/workspaces/{id}', [WorkspaceController::class, 'update']);
    Route::delete('/workspaces/{id}', [WorkspaceController::class, 'destroy']);
    Route::get('/workspaces/{workspaceId}/documents', [DocumentController::class, 'index']);
    Route::post('/workspaces/{workspaceId}/documents', [DocumentController::class, 'store']);
    Route::get('/documents/{documentId}', [DocumentController::class, 'show']);
    Route::delete('/documents/{documentId}', [DocumentController::class, 'destroy']);
    Route::get('/documents/{document}/view', [DocumentController::class, 'view']);
    Route::post('/documents/{documentId}/summarize', [DocumentController::class, 'summarize']);
    Route::post('/workspaces/{workspace}/share', [WorkspaceController::class, 'share']);
    Route::get('/workspaces/{workspace}/shared-users', [WorkspaceController::class, 'sharedUsers']);
    Route::delete('/workspaces/{workspace}/shared-users/{user}', [WorkspaceController::class, 'removeSharedUser']);
    Route::post('/conversations', [ConversationController::class, 'store']);
    Route::get('/workspaces/{workspaceId}/conversations', [ConversationController::class, 'index']);
    Route::get('/conversations/{conversationId}', [ConversationController::class, 'show']);
    Route::post('/conversations/{conversationId}/messages', [ConversationController::class, 'storeMessage']);
    Route::delete('/conversations/{conversationId}', [ConversationController::class, 'destroy']);
    

});

