import random
import uuid
from datetime import date, timedelta
import pandas as pd
from faker import Faker

fake = Faker("es_CO")
Faker.seed(42)
random.seed(42)

ESTADOS = ["ABIERTO", "EN PROCESO", "CERRADO", "EVALUACION"]
PESOS_ESTADO = [0.30, 0.35, 0.25, 0.10]
IDS_EMPRESA = [str(uuid.uuid4()) for _ in range(5)]
IDS_CATEGORIA = [str(uuid.uuid4()) for _ in range(5)]
IDS_PRIORIDAD = [str(uuid.uuid4()) for _ in range(3)]
FILAS = 500

TEMAS = [
    ("emprendimientos rurales", "brindar formación financiera y asistencia técnica"),
    ("educación digital", "mejorar el acceso a dispositivos y habilidades digitales"),
    ("acceso al agua potable", "ampliar la cobertura y el cuidado de fuentes hídricas"),
    ("turismo comunitario", "fortalecer la oferta turística y la economía local"),
    ("agricultura sostenible", "promover prácticas productivas sostenibles"),
    ("empleabilidad juvenil", "conectar a jóvenes con formación y oportunidades laborales"),
    ("conectividad rural", "mejorar el acceso a internet en zonas apartadas"),
    ("seguridad alimentaria", "apoyar la producción y distribución de alimentos"),
    ("formación técnica", "ofrecer capacitación según las necesidades del territorio"),
    ("gestión de residuos", "impulsar la separación y el aprovechamiento de residuos"),
]
LUGARES = [
    "Bogotá", "Medellín", "Cali", "Barranquilla", "Cartagena",
    "Bucaramanga", "Pasto", "Manizales", "Sincelejo", "Villavicencio",
]
FORMATOS_NOMBRE = [
    "Fortalecimiento de {tema} en {lugar}",
    "Iniciativa para impulsar {tema} en {lugar}",
    "Programa de apoyo a {tema} en {lugar}",
]
VARIANTES_ESTADO = {
    "ABIERTO": ["abierto", " ABIERTO "],
    "EN PROCESO": ["en proceso", " EN PROCESO "],
    "CERRADO": ["cerrado", " Cerrado "],
    "EVALUACION": ["evaluacion", " EVALUACION "],
}


def generar_muestra(datos_df, porcentaje):
    return datos_df.sample(
        frac=porcentaje,
        random_state=random.randint(1, 999),
    ).index


def generar_fechas(estado):
    """Genera fechas compatibles con el estado del reto."""
    hoy = date.today()

    if estado == "ABIERTO":
        fecha_inicio = fake.date_between(start_date="-3m", end_date="+3m")
        fecha_fin = max(fecha_inicio, hoy) + timedelta(days=random.randint(15, 180))
    elif estado == "EN PROCESO":
        fecha_inicio = fake.date_between(start_date="-1y", end_date="today")
        fecha_fin = hoy + timedelta(days=random.randint(15, 180))
    elif estado == "CERRADO":
        fecha_fin = fake.date_between(start_date="-1y", end_date="today")
        fecha_inicio = fecha_fin - timedelta(days=random.randint(15, 180))
    else:
        fecha_fin = fake.date_between(start_date="-3m", end_date="today")
        fecha_inicio = fecha_fin - timedelta(days=random.randint(15, 120))

    return fecha_inicio, fecha_fin


def generar_datos_limpios(n=FILAS):
    filas = []
    for _ in range(n):
        estado = random.choices(ESTADOS, weights=PESOS_ESTADO, k=1)[0]
        tema, objetivo = random.choice(TEMAS)
        lugar = random.choice(LUGARES)
        nombre = random.choice(FORMATOS_NOMBRE).format(tema=tema, lugar=lugar)
        descripcion = (
            f"El reto busca {objetivo} para {tema} en {lugar}, "
            "con seguimiento de resultados y participación de actores locales."
        )
        fecha_inicio, fecha_fin = generar_fechas(estado)
        filas.append({
            "id": str(uuid.uuid4()),
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "estado": estado,
            "id_empresa": random.choice(IDS_EMPRESA),
            "id_categoria": random.choice(IDS_CATEGORIA),
            "id_prioridad": random.choice(IDS_PRIORIDAD),
        })
    return pd.DataFrame(filas)


def ensuciar(datos_df):
    datos_df = datos_df.copy()
    datos_df["fecha_inicio"] = pd.to_datetime(datos_df["fecha_inicio"], errors="coerce")
    datos_df["fecha_fin"] = pd.to_datetime(datos_df["fecha_fin"], errors="coerce")

    # nombre: 10% con espacios sobrantes
    filas_elegidas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "nombre"] = " " + datos_df.loc[filas_elegidas, "nombre"] + " "

    # descripcion: 12% nulos (None)
    filas_elegidas = generar_muestra(datos_df, 0.12)
    datos_df.loc[filas_elegidas, "descripcion"] = None

    # fecha_fin: 8% nulos
    filas_elegidas = generar_muestra(datos_df, 0.08)
    datos_df.loc[filas_elegidas, "fecha_fin"] = None

    # fecha_fin: 5% anterior a fecha_inicio (error lógico a detectar)
    filas_con_fecha_fin = datos_df.index[datos_df["fecha_fin"].notna()]
    n_muestras = min(round(len(datos_df) * 0.05), len(filas_con_fecha_fin))
    if n_muestras > 0:
        filas_elegidas = datos_df.loc[filas_con_fecha_fin].sample(
            n=n_muestras, random_state=random.randint(1, 999)
        ).index
        datos_df.loc[filas_elegidas, "fecha_fin"] = [
            f_inicio - pd.Timedelta(days=random.randint(1, 30))
            for f_inicio in datos_df.loc[filas_elegidas, "fecha_inicio"]
        ]

    # fecha_inicio: mezclar formato ISO "2026-03-02" y latino "02/03/2026" (40% latino)
    iso = datos_df["fecha_inicio"].dt.strftime("%Y-%m-%d")
    latino = datos_df["fecha_inicio"].dt.strftime("%d/%m/%Y")
    datos_df["fecha_inicio"] = iso
    filas_elegidas = generar_muestra(datos_df, 0.40)
    datos_df.loc[filas_elegidas, "fecha_inicio"] = latino.loc[filas_elegidas]

    # estado: variantes de mayusculas y espacios en el 10% de las filas
    filas_elegidas = generar_muestra(datos_df, 0.10)
    datos_df.loc[filas_elegidas, "estado"] = [
        random.choice(VARIANTES_ESTADO[estado])
        for estado in datos_df.loc[filas_elegidas, "estado"]
    ]

    # Duplicar filas con la misma máscara de nulos para conservar sus porcentajes.
    n_duplicados = round(len(datos_df) * 0.05)
    if n_duplicados:
        grupos_por_nulos = {}
        for indice, fila in datos_df.iterrows():
            mascara_nulos = tuple(fila.isna())
            grupos_por_nulos.setdefault(mascara_nulos, []).append(indice)

        pares_disponibles = []
        for indices in grupos_por_nulos.values():
            random.shuffle(indices)
            pares_disponibles.extend(zip(indices[::2], indices[1::2]))

        if len(pares_disponibles) < n_duplicados:
            raise ValueError(
                f"No hay suficientes filas compatibles para crear "
                f"{n_duplicados} duplicados."
            )

        for destino, origen in random.sample(pares_disponibles, n_duplicados):
            datos_df.loc[destino] = datos_df.loc[origen].to_numpy()

    return datos_df


def generar_retos(n=FILAS):
    df = ensuciar(generar_datos_limpios(n))
    return df


if __name__ == "__main__":
    df = generar_retos()
    print(df.shape)
    print(df.head())
    print(df.isna().sum())