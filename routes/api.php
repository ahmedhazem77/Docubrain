<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\WorkspaceController;

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

});


