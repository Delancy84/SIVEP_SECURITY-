from database import vehiculos

datos = [

    {
        "placa":"ABC123",
        "propietario":"Juan Perez",
        "modelo":"Nissan Versa",
        "multas":0,
        "antecedentes":"No",
        "orden":"No"
    },

    {
        "placa":"XYZ789",
        "propietario":"Carlos Lopez",
        "modelo":"Honda Civic",
        "multas":3,
        "antecedentes":"No",
        "orden":"No"
    },

    {
        "placa":"TRD456",
        "propietario":"Miguel Torres",
        "modelo":"Chevrolet Aveo",
        "multas":1,
        "antecedentes":"Si",
        "orden":"Si"
    }

]

vehiculos.insert_many(datos)

print("Datos insertados correctamente")
