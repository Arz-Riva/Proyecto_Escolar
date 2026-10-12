// ==========================================
// Encabezados y Librerias
// ==========================================
#include "amortizacion.hpp"
#include <cmath>
#include <sstream>
#include <iomanip>

// ==========================================
// Declaracion de Funciones Auxiliares Privadas
// ==========================================
namespace {
    // Funcion privada auxiliar para redondear a 2 decimales
    double _redondear_dos_decimales(double val_numero) {
        return std::round(val_numero * 100.0) / 100.0;
    }
}

// ==========================================
// Implementacion de Funciones Puras de Calculo
// ==========================================

double calcular_tasa_mensual(double val_tasa_anual) {
    return (val_tasa_anual / FACTOR_PORCENTAJE) / MESES_EN_UN_ANIO;
}

// --- Sistema Frances ---

double calcular_cuota_fija_frances(double val_monto, double val_tasa_mensual, int num_meses_plazo) {
    if (num_meses_plazo <= 0) {
        return 0.0;
    }
    if (val_tasa_mensual <= 0.0) {
        return val_monto / num_meses_plazo;
    }
    
    // Formula financiera estandar: C = P * [ i*(1+i)^n ] / [ (1+i)^n - 1 ]
    double val_factor_potencia = std::pow(1.0 + val_tasa_mensual, num_meses_plazo);
    double val_cuota = val_monto * (val_tasa_mensual * val_factor_potencia) / (val_factor_potencia - 1.0);
    return val_cuota;
}

FilaTabla calcular_fila_frances(int num_mes, double val_saldo_actual, double val_tasa_mensual, double val_cuota_fija) {
    double val_interes = val_saldo_actual * val_tasa_mensual;
    double val_capital = val_cuota_fija - val_interes;
    double val_nuevo_saldo = val_saldo_actual - val_capital;
    
    // Ajuste de precision en los centavos residuales
    if (val_nuevo_saldo < 0.01) {
        val_capital = val_saldo_actual;
        val_cuota_fija = val_capital + val_interes;
        val_nuevo_saldo = 0.0;
    }
    
    return FilaTabla{
        num_mes,
        _redondear_dos_decimales(val_cuota_fija),
        _redondear_dos_decimales(val_interes),
        _redondear_dos_decimales(val_capital),
        _redondear_dos_decimales(val_nuevo_saldo)
    };
}

std::vector<FilaTabla> generar_tabla_frances(double val_monto, double val_tasa_mensual, int num_meses_plazo) {
    std::vector<FilaTabla> vec_tabla;
    if (num_meses_plazo <= 0 || val_monto <= 0.0) {
        return vec_tabla;
    }
    
    vec_tabla.reserve(num_meses_plazo);
    double val_cuota_fija = calcular_cuota_fija_frances(val_monto, val_tasa_mensual, num_meses_plazo);
    double val_saldo_actual = val_monto;
    
    for (int num_i = 1; num_i <= num_meses_plazo; ++num_i) {
        FilaTabla fila = calcular_fila_frances(num_i, val_saldo_actual, val_tasa_mensual, val_cuota_fija);
        vec_tabla.push_back(fila);
        val_saldo_actual = fila.val_saldo;
    }
    
    return vec_tabla;
}

// --- Sistema Aleman ---

FilaTabla calcular_fila_aleman(int num_mes, double val_saldo_actual, double val_tasa_mensual, double val_capital_fijo) {
    double val_interes = val_saldo_actual * val_tasa_mensual;
    double val_cuota = val_capital_fijo + val_interes;
    double val_nuevo_saldo = val_saldo_actual - val_capital_fijo;
    
    if (val_nuevo_saldo < 0.01) {
        val_nuevo_saldo = 0.0;
    }
    
    return FilaTabla{
        num_mes,
        _redondear_dos_decimales(val_cuota),
        _redondear_dos_decimales(val_interes),
        _redondear_dos_decimales(val_capital_fijo),
        _redondear_dos_decimales(val_nuevo_saldo)
    };
}

std::vector<FilaTabla> generar_tabla_aleman(double val_monto, double val_tasa_mensual, int num_meses_plazo) {
    std::vector<FilaTabla> vec_tabla;
    if (num_meses_plazo <= 0 || val_monto <= 0.0) {
        return vec_tabla;
    }
    
    vec_tabla.reserve(num_meses_plazo);
    double val_capital_fijo = val_monto / static_cast<double>(num_meses_plazo);
    double val_saldo_actual = val_monto;
    
    for (int num_i = 1; num_i <= num_meses_plazo; ++num_i) {
        FilaTabla fila = calcular_fila_aleman(num_i, val_saldo_actual, val_tasa_mensual, val_capital_fijo);
        vec_tabla.push_back(fila);
        val_saldo_actual = fila.val_saldo;
    }
    
    return vec_tabla;
}

// --- Sistema Americano ---

FilaTabla calcular_fila_americano(int num_mes, double val_monto_original, double val_tasa_mensual, int num_meses_plazo) {
    double val_interes = val_monto_original * val_tasa_mensual;
    double val_capital = 0.0;
    double val_cuota = val_interes;
    double val_saldo = val_monto_original;
    
    // En el ultimo mes se liquida la totalidad del capital prestado
    if (num_mes == num_meses_plazo) {
        val_capital = val_monto_original;
        val_cuota = val_capital + val_interes;
        val_saldo = 0.0;
    }
    
    return FilaTabla{
        num_mes,
        _redondear_dos_decimales(val_cuota),
        _redondear_dos_decimales(val_interes),
        _redondear_dos_decimales(val_capital),
        _redondear_dos_decimales(val_saldo)
    };
}

std::vector<FilaTabla> generar_tabla_americano(double val_monto, double val_tasa_mensual, int num_meses_plazo) {
    std::vector<FilaTabla> vec_tabla;
    if (num_meses_plazo <= 0 || val_monto <= 0.0) {
        return vec_tabla;
    }
    
    vec_tabla.reserve(num_meses_plazo);
    for (int num_i = 1; num_i <= num_meses_plazo; ++num_i) {
        FilaTabla fila = calcular_fila_americano(num_i, val_monto, val_tasa_mensual, num_meses_plazo);
        vec_tabla.push_back(fila);
    }
    
    return vec_tabla;
}

// --- Abonos extra a capital ---

double buscar_abono_mes(const std::vector<AbonoExtra>& vec_abonos, int num_mes) {
    double val_total = 0.0;
    for (const AbonoExtra& abono : vec_abonos) {
        if (abono.num_mes == num_mes && abono.val_monto > 0.0) {
            val_total += abono.val_monto;
        }
    }
    return val_total;
}

std::vector<AbonoExtra> parsear_abonos(const std::string& str_texto) {
    std::vector<AbonoExtra> vec_abonos;
    std::string str_token;
    std::istringstream ss_entrada(str_texto);
    // Formato esperado: "mes:monto,mes:monto" (ej. "3:1000,6:500")
    while (std::getline(ss_entrada, str_token, ',')) {
        std::size_t pos_separador = str_token.find(':');
        if (pos_separador == std::string::npos) {
            continue;
        }
        try {
            int num_mes = std::stoi(str_token.substr(0, pos_separador));
            double val_monto = std::stod(str_token.substr(pos_separador + 1));
            if (num_mes >= 1 && val_monto > 0.0) {
                vec_abonos.push_back(AbonoExtra{num_mes, val_monto});
            }
        } catch (...) {
            continue;
        }
    }
    return vec_abonos;
}

std::vector<FilaTabla> generar_tabla_frances_con_abonos(double val_monto, double val_tasa_mensual, int num_meses_plazo, const std::vector<AbonoExtra>& vec_abonos) {
    if (vec_abonos.empty()) {
        return generar_tabla_frances(val_monto, val_tasa_mensual, num_meses_plazo);
    }
    std::vector<FilaTabla> vec_tabla;
    if (num_meses_plazo <= 0 || val_monto <= 0.0) {
        return vec_tabla;
    }
    vec_tabla.reserve(num_meses_plazo);
    double val_cuota_fija = calcular_cuota_fija_frances(val_monto, val_tasa_mensual, num_meses_plazo);
    double val_saldo_actual = val_monto;
    for (int num_i = 1; num_i <= num_meses_plazo; ++num_i) {
        if (val_saldo_actual <= 0.005) {
            break;
        }
        FilaTabla fila = calcular_fila_frances(num_i, val_saldo_actual, val_tasa_mensual, val_cuota_fija);
        double val_extra = buscar_abono_mes(vec_abonos, num_i);
        if (val_extra > 0.0 && fila.val_saldo > 0.0) {
            double val_aplicado = std::min(val_extra, fila.val_saldo);
            fila.val_capital = _redondear_dos_decimales(fila.val_capital + val_aplicado);
            fila.val_cuota = _redondear_dos_decimales(fila.val_cuota + val_aplicado);
            fila.val_saldo = _redondear_dos_decimales(fila.val_saldo - val_aplicado);
        }
        vec_tabla.push_back(fila);
        val_saldo_actual = fila.val_saldo;
    }
    return vec_tabla;
}

std::vector<FilaTabla> generar_tabla_aleman_con_abonos(double val_monto, double val_tasa_mensual, int num_meses_plazo, const std::vector<AbonoExtra>& vec_abonos) {
    if (vec_abonos.empty()) {
        return generar_tabla_aleman(val_monto, val_tasa_mensual, num_meses_plazo);
    }
    std::vector<FilaTabla> vec_tabla;
    if (num_meses_plazo <= 0 || val_monto <= 0.0) {
        return vec_tabla;
    }
    vec_tabla.reserve(num_meses_plazo);
    double val_capital_fijo = val_monto / static_cast<double>(num_meses_plazo);
    double val_saldo_actual = val_monto;
    for (int num_i = 1; num_i <= num_meses_plazo; ++num_i) {
        if (val_saldo_actual <= 0.005) {
            break;
        }
        FilaTabla fila = calcular_fila_aleman(num_i, val_saldo_actual, val_tasa_mensual, val_capital_fijo);
        // Ajuste si el capital fijo supera el saldo restante tras los abonos
        if (fila.val_capital > val_saldo_actual) {
            fila.val_capital = _redondear_dos_decimales(val_saldo_actual);
            fila.val_cuota = _redondear_dos_decimales(fila.val_capital + fila.val_interes);
            fila.val_saldo = 0.0;
        }
        double val_extra = buscar_abono_mes(vec_abonos, num_i);
        if (val_extra > 0.0 && fila.val_saldo > 0.0) {
            double val_aplicado = std::min(val_extra, fila.val_saldo);
            fila.val_capital = _redondear_dos_decimales(fila.val_capital + val_aplicado);
            fila.val_cuota = _redondear_dos_decimales(fila.val_cuota + val_aplicado);
            fila.val_saldo = _redondear_dos_decimales(fila.val_saldo - val_aplicado);
        }
        vec_tabla.push_back(fila);
        val_saldo_actual = fila.val_saldo;
    }
    return vec_tabla;
}

std::vector<FilaTabla> generar_tabla_americano_con_abonos(double val_monto, double val_tasa_mensual, int num_meses_plazo, const std::vector<AbonoExtra>& vec_abonos) {
    if (vec_abonos.empty()) {
        return generar_tabla_americano(val_monto, val_tasa_mensual, num_meses_plazo);
    }
    std::vector<FilaTabla> vec_tabla;
    if (num_meses_plazo <= 0 || val_monto <= 0.0) {
        return vec_tabla;
    }
    vec_tabla.reserve(num_meses_plazo);
    double val_saldo_actual = val_monto;
    for (int num_i = 1; num_i <= num_meses_plazo; ++num_i) {
        if (val_saldo_actual <= 0.005) {
            break;
        }
        double val_interes = _redondear_dos_decimales(val_saldo_actual * val_tasa_mensual);
        double val_extra = buscar_abono_mes(vec_abonos, num_i);
        double val_capital = 0.0;
        double val_cuota = val_interes;
        double val_nuevo_saldo = val_saldo_actual;
        // En el ultimo mes se liquida todo el saldo restante
        if (num_i == num_meses_plazo) {
            val_capital = val_saldo_actual;
            val_cuota = _redondear_dos_decimales(val_capital + val_interes);
            val_nuevo_saldo = 0.0;
        } else if (val_extra > 0.0) {
            double val_aplicado = std::min(val_extra, val_saldo_actual);
            val_capital = _redondear_dos_decimales(val_aplicado);
            val_cuota = _redondear_dos_decimales(val_interes + val_aplicado);
            val_nuevo_saldo = _redondear_dos_decimales(val_saldo_actual - val_aplicado);
        }
        vec_tabla.push_back(FilaTabla{num_i, val_cuota, val_interes, val_capital, val_nuevo_saldo});
        val_saldo_actual = val_nuevo_saldo;
    }
    return vec_tabla;
}

// ==========================================
// Utilerias de Serializacion a JSON
// ==========================================

std::string serializar_tabla_json(const std::vector<FilaTabla>& vec_tabla) {
    std::ostringstream ss_salida;
    ss_salida << std::fixed << std::setprecision(2);
    ss_salida << "[\n";
    
    for (size_t num_idx = 0; num_idx < vec_tabla.size(); ++num_idx) {
        const FilaTabla& fila = vec_tabla[num_idx];
        ss_salida << "  {\n"
                  << "    \"mes\": " << fila.num_mes << ",\n"
                  << "    \"cuota\": " << fila.val_cuota << ",\n"
                  << "    \"interes\": " << fila.val_interes << ",\n"
                  << "    \"capital\": " << fila.val_capital << ",\n"
                  << "    \"saldo\": " << fila.val_saldo << "\n"
                  << "  }";
        
        if (num_idx + 1 < vec_tabla.size()) {
            ss_salida << ",";
        }
        ss_salida << "\n";
    }
    
    ss_salida << "]";
    return ss_salida.str();
}
