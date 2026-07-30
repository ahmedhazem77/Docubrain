<?php

namespace App\Jobs;

use App\Models\Document;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;

class ProcessDocumentJob implements ShouldQueue
{
    use Queueable;

    protected Document $document;

    public function __construct(Document $document)
    {
        $this->document = $document;
    }

    public function handle(): void
{
    try {
        // Simulate processing
        sleep(5); // 5 second delay to simulate processing time

        $this->document->update([
            'status' => 'processed',
        ]);
    } catch (\Throwable $e) {
        $this->document->update([
            'status' => 'failed',
        ]);

        throw $e; 
    }
}
}