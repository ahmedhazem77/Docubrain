# System overview:
DocuBrain is a web document management application that enables authenticated users to organize and manage documents using workspaces. Users can register, log in, create multiple workspaces, upload documents, and monitor the processing status of their uploaded files.

# High-Level Architecture:

                    |-----------------------|
                    |        User           |
                    |-----------------------|
                                |
                                |
                                v
                    |-----------------------|
                    |        Frontend       |
                    |-----------------------|
                                |
                         REST API Requests
                                |
                                v
                    |-----------------------|
                    |        Backend        |
                    |-----------------------|
                                |
                  -----------------------------
                  |                           |
                  v                           v
      |---------------------|     |----------------------|
      |      Database       |     |   File Storage       |
      |---------------------|     |----------------------|


   # Database Design:
   
   # 1.Users:
-------------------------       
| Field     | Type      |
|-----------------------|
| id        |     PK    | (Primary Key)
| name      |   String  |
| email     |   String  |
| password  |   String  |
| created at| Timestamp |
| updated at| Timestamp |           
-------------------------

   # 2.Workspaces:
-------------------------       
| Field     | Type      |
|-----------------------|
| id        |     PK    | (Primary Key)
| user_id   |     FK    | (Foreign Key references users.id)
| name      |   String  |  
|description|   Text    | (nullable)
| created at| Timestamp |
| updated at| Timestamp |           
-------------------------


   # 3.Documents:
-------------------------       
| Field     | Type      |
|-----------------------|
| id        |     PK    | (Primary Key)
|workspace_id|    FK    | (Foreign Key references workspace.id)
| file_name |   String  |
| file_path |   String  |
| status    |   Enum    | [Pending,Processed,Failed]
| metadata  |Json Binary|           
|created_at | Timestamp |
|updated at | Timestamp |
-------------------------


# Entity Relationships:

|-----------|
|   Users   |
|-----------|
| id        |
| name      |
| email     |                                
| password  |
| timestamp |
|-----------|
      |
      | 1
      |
      |     (One to Many relationship: user can have mltiple workspaces,while a work space only belongs to one user)
      |
      | *
|-------------|
| Workspaces  |
|-------------|
| id          |
| user_id     |
| name        |
| description |
| timestamp   |
|-------------|
      | 1
      |   (one to many)
      |
      | *
|-------------|
| Documents   |
|-------------|
| id          |
| workspace_id|
| file_name   |
| file_path   |
| status      |
| metadata    |
| timestamp   |
|-------------|



# API Routes:
| Route                                 | Purpose                | Requires Authentication |
| ------------------------------------- | ---------------------- | ------------------------|                  
| POST `/api/register`                  | Create user            |         No              |
| POST `/api/login`                     | Log in                 |         No              |
| GET `/api/workspaces`                 | List user's workspaces |         Yes             |
| POST `/api/workspaces`                | Create workspace       |         Yes             |
| POST `/api/workspaces/{id}/documents` | Upload document        |         Yes             |
  


# Workflow Description:

1. The authenticated user selects a document to upload.
2. The Vue frontend sends the file as a multipart/form-data request to the Laravel API.
3. Laravel validates the request and stores the uploaded file on the server.
4. A document record is created in PostgreSQL with its metadata and an initial status of Pending
5. The backend dispatches a background queue job ProcessDocumentJob.
6. After processing is completed, the document status is updated to Processed.