resource "aws_glue_catalog_database" "sparkskew-db" {
  name = "sparkskew_db"

  catalog_id   = local.catalog_id
  location_uri = "s3://${aws_s3_bucket.sparkskew.bucket}/"
}

resource "aws_glue_catalog_table" "orders_v1" {
  name        = "orders_v1"
  description = "Raw table for order events with balanced skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  partition_keys {
    name = "event_date"
    type = "string"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/orders_v1/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "order_id"
      type = "bigint"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "product_id"
      type = "bigint"
    }

    columns {
      name = "order_timestamp"
      type = "timestamp"
    }

    columns {
      name = "quantity"
      type = "int"
    }

    columns {
      name = "unit_price"
      type = "decimal(12,2)"
    }

    columns {
      name = "event_type"
      type = "string"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }
}

resource "aws_glue_catalog_table" "orders_v2" {
  name        = "orders_v2"
  description = "Raw table for order events with low skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  partition_keys {
    name = "event_date"
    type = "string"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/orders_v2/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "order_id"
      type = "bigint"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "product_id"
      type = "bigint"
    }

    columns {
      name = "order_timestamp"
      type = "timestamp"
    }

    columns {
      name = "quantity"
      type = "int"
    }

    columns {
      name = "unit_price"
      type = "decimal(12,2)"
    }

    columns {
      name = "event_type"
      type = "string"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }
}

resource "aws_glue_catalog_table" "orders_v3" {
  name        = "orders_v3"
  description = "Raw table for order events with high skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  partition_keys {
    name = "event_date"
    type = "string"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/orders_v3/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "order_id"
      type = "bigint"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "product_id"
      type = "bigint"
    }

    columns {
      name = "order_timestamp"
      type = "timestamp"
    }

    columns {
      name = "quantity"
      type = "int"
    }

    columns {
      name = "unit_price"
      type = "decimal(12,2)"
    }

    columns {
      name = "event_type"
      type = "string"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }
}

resource "aws_glue_catalog_table" "customers_v1" {
  name        = "customers_v1"
  description = "Raw table for customers with balanced skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/customers_v1/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "customer_name"
      type = "string"
    }

    columns {
      name = "customer_segment"
      type = "string"
    }

    columns {
      name = "country_code"
      type = "string"
    }

    columns {
      name = "created_at"
      type = "timestamp"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    external       = "TRUE"
  }
}

resource "aws_glue_catalog_table" "customers_v2" {
  name        = "customers_v2"
  description = "Raw table for customers with balanced skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/customers_v2/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "customer_name"
      type = "string"
    }

    columns {
      name = "customer_segment"
      type = "string"
    }

    columns {
      name = "country_code"
      type = "string"
    }

    columns {
      name = "created_at"
      type = "timestamp"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    external       = "TRUE"
  }
}

resource "aws_glue_catalog_table" "customers_v3" {
  name        = "customers_v3"
  description = "Raw table for customers with balanced skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/customers_v3/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "customer_name"
      type = "string"
    }

    columns {
      name = "customer_segment"
      type = "string"
    }

    columns {
      name = "country_code"
      type = "string"
    }

    columns {
      name = "created_at"
      type = "timestamp"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    external       = "TRUE"
  }
}

resource "aws_glue_catalog_table" "orders_test" {
  name        = "orders_test"
  description = "Raw table for order events with high skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  partition_keys {
    name = "event_date"
    type = "string"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/orders_test/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "order_id"
      type = "bigint"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "product_id"
      type = "bigint"
    }

    columns {
      name = "order_timestamp"
      type = "timestamp"
    }

    columns {
      name = "quantity"
      type = "int"
    }

    columns {
      name = "unit_price"
      type = "decimal(12,2)"
    }

    columns {
      name = "event_type"
      type = "string"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }
}

resource "aws_glue_catalog_table" "customers_test" {
  name        = "customers_test"
  description = "Raw table for customers with balanced skew."

  catalog_id    = local.catalog_id
  database_name = aws_glue_catalog_database.sparkskew-db.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.sparkskew.bucket}/customers_test/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "customer_id"
      type = "bigint"
    }

    columns {
      name = "customer_name"
      type = "string"
    }

    columns {
      name = "customer_segment"
      type = "string"
    }

    columns {
      name = "country_code"
      type = "string"
    }

    columns {
      name = "created_at"
      type = "timestamp"
    }

    columns {
      name = "ingested_at"
      type = "date"
    }
  }

  parameters = {
    classification = "parquet"
    external       = "TRUE"
  }
}
