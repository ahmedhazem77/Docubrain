<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Document extends Model
{
  protected $fillable = [
        'workspace_id',
        'file_name',
        'file_path',
        'status',
        'metadata',
    ];

    protected $casts = [
    'metadata' => 'array',
];

    public function workspace()
    {
        return $this->belongsTo(Workspace::class);
    }
}
