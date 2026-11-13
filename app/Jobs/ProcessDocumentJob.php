<?php

namespace App\Jobs;

use App\Models\Document;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;

class ProcessDocumentJob implements ShouldQueue
{
    use Queueable;
     
    # Job receives a document
    protected Document $document;

    public function __construct(Document $document)
    {
        $this->document = $document;
    }

    public function handle(): void
    {
        try {
            $filePath = Storage::path($this->document->file_path);

            if (!file_exists($filePath)) {
                throw new \Exception(
                    "Document file not found: {$filePath}"
                );
            }  


             #Laravel sends the file to the AI Engine for processing. The AI Engine will read the PDF, extract text, generate embeddings, and store them in PostgreSQL. 
            $response = Http::timeout(300)
                ->attach(
                    'file',
                    fopen($filePath, 'r'),
                    $this->document->file_name
                )
                ->post(rtrim(config('services.ai_engine.url'), '/').'/process-document', [
                    'document_id' => $this->document->id,
                    'workspace_id' => $this->document->workspace_id,
                ]);

            if ($response->failed()) {
                throw new \Exception(
                    'AI Engine failed: ' . $response->body()
                );
            }

          $responseData = $response->json();

             $this->document->update([
               'status' => $responseData['status'] ?? 'processed',
                  ]);

        } catch (\Throwable $e) {

            $this->document->update([
                'status' => 'failed',
            ]);

            throw $e;
        }
    }
}