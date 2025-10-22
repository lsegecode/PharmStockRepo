from django.db import models

class Insumo(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    codigo = models.CharField(max_length=100, db_column='codigo', unique=True)
    descripcion = models.CharField(max_length=255, db_column='descripcion')
    punto_pedido = models.BigIntegerField(db_column='PuntoPedido', null=True, blank=True)
    stock_ideal = models.BigIntegerField(db_column='StockIdeal', null=True, blank=True)
    stock_critico = models.BigIntegerField(db_column='StockCritico', null=True, blank=True)

    class Meta:
        managed = False
        db_table = '[farm].[Insumos]'

    def __str__(self):
        return f'{self.codigo} - {self.descripcion}'


class StockFarmCentral(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    fk_codigo_insumo = models.CharField(max_length=100, db_column='fk_codigo_insumo')
    cantidad_existente = models.BigIntegerField(db_column='cantidad_existente')

    class Meta:
        managed = False
        db_table = '[farm].[Stock_farm_central]'

    @property
    def insumo(self):
        try:
            return Insumo.objects.get(codigo=self.fk_codigo_insumo)
        except Insumo.DoesNotExist:
            return None


class StockMaletin(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    fk_codigo_insumo = models.CharField(max_length=100, db_column='fk_codigo_insumo')
    funcion = models.CharField(max_length=5, db_column='funcion')
    cantidad_existente = models.BigIntegerField(db_column='cantidad_existente')
    cantidad_ideal = models.BigIntegerField(db_column='cantidad_ideal')

    class Meta:
        managed = False
        db_table = '[farm].[Stock_maletin]'

    @property
    def insumo(self):
        try:
            return Insumo.objects.get(codigo=self.fk_codigo_insumo)
        except Insumo.DoesNotExist:
            return None


class StockMaletinMov(models.Model):
    id = models.BigAutoField(primary_key=True, db_column='id')
    fk_codigo_insumo = models.CharField(max_length=100, db_column='fk_codigo_insumo')
    fecha_mov = models.DateTimeField(db_column='fecha_mov')
    funcion = models.CharField(max_length=5, db_column='funcion')
    fk_tipo_movimiento = models.IntegerField(db_column='fk_tipo_movimiento')
    usuario_mod = models.TextField(db_column='usuario_mod')
    descripcion = models.TextField(db_column='descripcion')
    cantidad_operacion = models.BigIntegerField(db_column='cantidad_operacion')
    cantidad_inicial = models.BigIntegerField(db_column='cantidad_inicial')

    class Meta:
        managed = False
        db_table = '[farm].[Stock_maletin_Mov]'
