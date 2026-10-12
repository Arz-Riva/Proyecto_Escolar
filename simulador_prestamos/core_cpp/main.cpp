// ==========================================
// Encabezados y Librerias
// ==========================================
#include "amortizacion.hpp"
#include <iostream>
#include <string>
#include <algorithm>
#include <cctype>

// ==========================================
// Declaracion de Funciones Auxiliares
// ==========================================
namespace {
    // Convierte una cadena de texto a minusculas para comparaciones estandarizadas
    std::string _convertir_minusculas(std::string str_texto) {
        std::transform(str_texto.begin(), str_texto.end(), str_texto.begin(), [](unsigned char c) {
            return static_cast<char>(std::tolower(c));
        });
        return str_texto;
    }
}

// ==========================================
// Proceso Principal (CLI / Imperative Shell)
// ==========================================

int main(int argc, char* argv[]) {
    // Validacion de argumentos esperados: <sistema> <monto> <tasa_anual> <meses> [abonos]
    if (argc < 5) {
        std::cout << "{\n  \"error\": \"Argumentos insuficientes. Uso: amortizador <sistema> <monto> <tasa_anual> <meses> [abonos mes:monto,mes:monto]\"\n}\n";
        return 1;
    }

    try {
        std::string str_sistema = _convertir_minusculas(argv[1]);
        double val_monto = std::stod(argv[2]);
        double val_tasa_anual = std::stod(argv[3]);
        int num_meses_plazo = std::stoi(argv[4]);
        // Quinto argumento opcional con abonos: "mes:monto,mes:monto"
        std::vector<AbonoExtra> vec_abonos;
        if (argc >= 6) {
            vec_abonos = parsear_abonos(argv[5]);
        }

        // Validacion de rangos numericos validos
        if (val_monto <= 0.0 || num_meses_plazo <= 0 || val_tasa_anual < 0.0) {
            std::cout << "{\n  \"error\": \"Parametros numericos invalidos. El monto y meses deben ser mayores a 0, y la tasa positiva.\"\n}\n";
            return 1;
        }
        for (const AbonoExtra& abono : vec_abonos) {
            if (abono.num_mes > num_meses_plazo) {
                std::cout << "{\n  \"error\": \"Abono fuera de plazo. El mes debe estar entre 1 y los meses del credito.\"\n}\n";
                return 1;
            }
        }

        double val_tasa_mensual = calcular_tasa_mensual(val_tasa_anual);
        std::vector<FilaTabla> vec_resultado;
        bool con_abonos = !vec_abonos.empty();

        // Seleccion del sistema de amortizacion
        if (str_sistema == "frances" || str_sistema == "francés") {
            vec_resultado = con_abonos
                ? generar_tabla_frances_con_abonos(val_monto, val_tasa_mensual, num_meses_plazo, vec_abonos)
                : generar_tabla_frances(val_monto, val_tasa_mensual, num_meses_plazo);
        } else if (str_sistema == "aleman" || str_sistema == "alemán") {
            vec_resultado = con_abonos
                ? generar_tabla_aleman_con_abonos(val_monto, val_tasa_mensual, num_meses_plazo, vec_abonos)
                : generar_tabla_aleman(val_monto, val_tasa_mensual, num_meses_plazo);
        } else if (str_sistema == "americano") {
            vec_resultado = con_abonos
                ? generar_tabla_americano_con_abonos(val_monto, val_tasa_mensual, num_meses_plazo, vec_abonos)
                : generar_tabla_americano(val_monto, val_tasa_mensual, num_meses_plazo);
        } else {
            std::cout << "{\n  \"error\": \"Sistema desconocido. Opciones validas: frances, aleman, americano\"\n}\n";
            return 1;
        }

        // Salida estandar en formato JSON puro
        std::string str_json = serializar_tabla_json(vec_resultado);
        std::cout << str_json << std::endl;
        return 0;

    } catch (const std::exception& obj_error) {
        std::cout << "{\n  \"error\": \"Error al procesar argumentos: " << obj_error.what() << "\"\n}\n";
        return 1;
    }
}
