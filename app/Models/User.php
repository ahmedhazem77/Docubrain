<?php

namespace App\Models;

// use Illuminate\Contracts\Auth\MustVerifyEmail;
use Laravel\Sanctum\HasApiTokens;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'name',
        'email',
        'password',
    ];

    public function workspaces(){
        return $this->hasMany(Workspace::class);
    }

    public function sharedWorkspaces()
    {
        return $this->belongsToMany(Workspace::class, 'workspace_user')
            ->withPivot('role')
            ->withTimestamps();
    }

    public function findAccessibleWorkspace($id): ?Workspace
    {
        $owned = $this->workspaces()->find($id);

        if ($owned) {
            $owned->setAttribute('role', 'owner');
            $owned->setAttribute('is_owner', true);
            return $owned;
        }

        $shared = $this->sharedWorkspaces()->find($id);

        if ($shared) {
            $shared->setAttribute('role', $shared->pivot->role);
            $shared->setAttribute('is_owner', false);
            return $shared;
        }

        return null;
    }



    /**
     * The attributes that should be hidden for serialization.
     *
     * @var array<int, string>
     */
    protected $hidden = [
        'password',
        'remember_token',
    ];

    /**
     * Get the attributes that should be cast.
     *
     * @return array<string, string>
     */
    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
        ];
    }

    public function conversations()
{
    return $this->hasMany(Conversation::class);
}
}
