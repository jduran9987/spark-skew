resource "aws_glue_catalog_database" "sparkskew-db" {
  name = "sparkskew_db"

  location_uri = "s3://${aws_s3_bucket.lakehouse.bucket}/"
}

resource "aws_glue_catalog_table" "orders" {
  name        = "orders"
  description = "Raw table for order events."

  database_name = aws_glue_catalog_database.spark-skew-db.name
}
