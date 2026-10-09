/*
Corrige GETTABLE_RE_BOLETAS_CABECERA_WEB_ASL para octubre-diciembre.

La columna temporal mes_pago es varchar y recibe A/B/C. Compararla después
con enteros obliga a SQL Server a convertir A a int y produce el error 245.
Las comparaciones deben ser entre cadenas.
*/

DECLARE @definition nvarchar(max) = OBJECT_DEFINITION(
    OBJECT_ID(N'dbo.GETTABLE_RE_BOLETAS_CABECERA_WEB_ASL')
);

IF @definition IS NULL
    THROW 50001, 'No existe GETTABLE_RE_BOLETAS_CABECERA_WEB_ASL.', 1;

SET @definition = REPLACE(@definition, 'CREATE procedure', 'ALTER procedure');
SET @definition = REPLACE(@definition, 'CREATE PROCEDURE', 'ALTER PROCEDURE');
SET @definition = REPLACE(@definition, 'where mes_pago = 10', 'where mes_pago = ''10''');
SET @definition = REPLACE(@definition, 'where mes_pago = 11', 'where mes_pago = ''11''');
SET @definition = REPLACE(@definition, 'where mes_pago = 12', 'where mes_pago = ''12''');

IF @definition NOT LIKE '%where mes_pago = ''10''%'
    THROW 50002, 'No se pudo preparar la corrección de mes_pago.', 1;

EXEC sys.sp_executesql @definition;
