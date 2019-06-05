TODO

- This is mainly for production. Does not work with `tutor dev` commands.
- For local testing, you need to set MINIO_HOST to minio.localhost:

    tutor config save --set MINIO_HOST=minio.localhost
  
- You need `minio.LMS_HOST` domain name. For local development, the MinIO admin dashboard is at minio.localhost. For authentication, use MINIO_ACCESS_KEY and MINIO_SECRET_KEY:

    tutor config printvalue OPENEDX_AWS_ACCESS_KEY
    tutor config printvalue OPENEDX_AWS_SECRET_ACCESS_KEY