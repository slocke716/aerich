from typing import Type

from tortoise import Model
from tortoise.backends.asyncpg.schema_generator import AsyncpgSchemaGenerator
from tortoise.fields import Field

from aerich.ddl import BaseDDL


class PostgresDDL(BaseDDL):
    schema_generator_cls = AsyncpgSchemaGenerator
    DIALECT = AsyncpgSchemaGenerator.DIALECT
    _ALTER_DEFAULT_TEMPLATE = 'ALTER TABLE "{table_name}" ALTER COLUMN "{column}" {default}'
    _ALTER_NULL_TEMPLATE = 'ALTER TABLE "{table_name}" ALTER COLUMN "{column}" {set_drop} NOT NULL'
    _MODIFY_COLUMN_TEMPLATE = 'ALTER TABLE "{table_name}" ALTER COLUMN "{column}" TYPE {datatype}'
    _SET_COMMENT_TEMPLATE = 'COMMENT ON COLUMN "{table_name}"."{column}" IS {comment}'

    def alter_column_default(self, model: "Type[Model]", field_object: Field):
        db_table = model._meta.db_table
        default = self._get_default(model, field_object)
        return self._ALTER_DEFAULT_TEMPLATE.format(
            table_name=db_table,
            column=field_object.model_field_name,
            default="SET" + default if default else "DROP DEFAULT",
        )

    def alter_column_null(self, model: "Type[Model]", field_object: Field):
        db_table = model._meta.db_table
        return self._ALTER_NULL_TEMPLATE.format(
            table_name=db_table,
            column=field_object.model_field_name,
            set_drop="DROP" if field_object.null else "SET",
        )

    def modify_column(self, model: "Type[Model]", field_object: Field):
        db_table = model._meta.db_table
        return self._MODIFY_COLUMN_TEMPLATE.format(
            table_name=db_table,
            column=field_object.model_field_name,
            datatype=field_object.get_for_dialect(self.DIALECT, "SQL_TYPE"),
        )

    def set_comment(self, model: "Type[Model]", field_object: Field):
        db_table = model._meta.db_table
        return self._SET_COMMENT_TEMPLATE.format(
            table_name=db_table,
            column=field_object.model_field_name,
            comment="'{}'".format(field_object.description) if field_object.description else "NULL",
        )
