import csv
import logging
from datetime import datetime

# Configuración de Logs
logging.basicConfig(
    filename='validacion.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='w'
)

file_path = 'ventas_sucias.csv'


class DataValidator:
    def __init__(self, file_path):
        with open(file_path, mode='r', encoding='utf-8-sig', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            self.fieldnames = reader.fieldnames or []
            self.rows = [dict(row) for row in reader]
        self.errors = []
        self.valid_df = []
        self.invalid_df = []

    def _log_error(self, index, row, reason):
        error_msg = f"Fila {index} (ID: {row.get('id', '')}): {reason}"
        logging.warning(error_msg)
        self.errors.append({'index': index, 'id': row.get('id', ''), 'motivo': reason})

    def validate_structural(self):
        """
        Validaciones Estructurales:
        1. IDs Duplicados.
        2. Valores faltantes en campos críticos.
        3. Consistencia de tipos (numéricos).
        """
        indices_to_drop = set()
        seen_ids = set()

        # 1. IDs Duplicados
        for idx, row in enumerate(self.rows):
            row_id = row.get('id', '')
            if row_id in seen_ids:
                self._log_error(idx, row, "ID Duplicado detectado")
                indices_to_drop.add(idx)
            else:
                seen_ids.add(row_id)

        # 2. Valores Vacíos (detecta espacios en blanco o NaNs)
        for col in ['nombre', 'monto', 'edad']:
            for idx, row in enumerate(self.rows):
                if idx in indices_to_drop:
                    continue
                value = row.get(col, '')
                if value is None or str(value).strip() == "":
                    self._log_error(idx, row, f"Campo obligatorio vacío: {col}")
                    indices_to_drop.add(idx)

        # 3. Verificación de tipo Numérico (Monto)
        for idx, row in enumerate(self.rows):
            if idx not in indices_to_drop:
                try:
                    float(row.get('monto', ''))
                except (TypeError, ValueError):
                    self._log_error(idx, row, f"Monto '{row.get('monto', '')}' no es un número válido")
                    indices_to_drop.add(idx)

        return indices_to_drop

    def validate_semantic(self, structural_indices):
        """
        Validaciones Semánticas:
        1. Rango de Edad (0-120 años).
        2. Validez lógica de la fecha (calendario real).
        """
        indices_to_drop = structural_indices.copy()

        for idx, row in enumerate(self.rows):
            if idx in indices_to_drop:
                continue

            # 1. Rango de Edad
            try:
                edad = int(row.get('edad', ''))
            except (TypeError, ValueError):
                self._log_error(idx, row, f"Edad inválida: {row.get('edad', '')}")
                indices_to_drop.add(idx)
                continue

            if edad < 0 or edad > 120:
                self._log_error(idx, row, f"Edad fuera de rango lógico: {edad}")
                indices_to_drop.add(idx)
                continue

            # 2. Validez de Fecha (Ej: evita meses como el 13)
            date_str = str(row.get('fecha_compra', ''))
            valid_date = False
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    datetime.strptime(date_str, fmt)
                    valid_date = True
                    break
                except ValueError:
                    continue

            if not valid_date:
                self._log_error(idx, row, f"Fecha inexistente o formato inválido: {date_str}")
                indices_to_drop.add(idx)

        return indices_to_drop

    def run(self):
        struct_idx = self.validate_structural()
        all_bad_idx = self.validate_semantic(struct_idx)

        # Separación de registros
        self.invalid_df = [row for idx, row in enumerate(self.rows) if idx in all_bad_idx]
        self.valid_df = [row.copy() for idx, row in enumerate(self.rows) if idx not in all_bad_idx]

        # Estandarización de datos válidos
        for row in self.valid_df:
            if 'ciudad' in row and row['ciudad'] is not None:
                row['ciudad'] = str(row['ciudad']).title().strip()
            if 'metodo_pago' in row and row['metodo_pago'] is not None:
                row['metodo_pago'] = str(row['metodo_pago']).lower().strip()

        # Guardar resultados
        with open('registros_validos.csv', mode='w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(self.valid_df)

        with open('registros_erroneos.csv', mode='w', encoding='utf-8', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(self.invalid_df)

        print(f"Proceso finalizado. Válidos: {len(self.valid_df)} | Erróneos: {len(self.invalid_df)}")


if __name__ == "__main__":
    validador = DataValidator('ventas_sucias.csv')
    validador.run()