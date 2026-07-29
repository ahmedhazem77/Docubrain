<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Document extends Model
{
    protected $fillable = [
    'file_name',
];

    public function workspace()
    {
        return $this->belongsTo(Workspace::class);
    }
}
