#ifndef AMORTIZACION_HPP
#define AMORTIZACION_HPP

// ==========================================
// Encabezados y Librerias
// ==========================================
#include <vector>
#include <string>

// ==========================================
// Declaracion de Estructuras y Tipos
// ==========================================

// Representa una fila individual en la tabla de amortizacion
struct FilaTabla {
    int num_mes;
    double val_cuota;
    double val_interes;
    double val_capital;
    double val_saldo;
};

// Representa un abono extra a capital en un mes puntual
struct AbonoExtra {
    int num_mes;
    double val_monto;
};

// ==========================================
// Declaracion de Funciones Puras de Calculo
// ==========================================

// Constantes globales de conversion financiera
constexpr double MESES_EN_UN_ANIO = 12.0;
constexpr double FACTOR_PORCENTAJE = 100.0;

// Conversion de tasa de interes anual porcentual a tasa mensual decimal
double calcular_tasa_mensual(double val_tasa_anual);

// --- Sistema Frances (Cuota fija) ---
double calcular_cuota_fija_frances(double val_monto, double val_tasa_mensual, int num_meses_plazo);
FilaTabla calcular_fila_frances(int num_mes, double val_saldo_actual, double val_tasa_mensual, double val_cuota_fija);
std::vector<FilaTabla> generar_tabla_frances(double val_monto, double val_tasa_mensual, int num_meses_plazo);

// --- Sistema Aleman (Amortizacion de capital fijo) ---
FilaTabla calcular_fila_aleman(int num_mes, double val_saldo_actual, double val_tasa_mensual, double val_capital_fijo);
std::vector<FilaTabla> generar_tabla_aleman(double val_monto, double val_tasa_mensual, int num_meses_plazo);

// --- Sistema Americano (Interes periodico y capital al final) ---
FilaTabla calcular_fila_americano(int num_mes, double val_monto_original, double val_tasa_mensual, int num_meses_plazo);
std::vector<FilaTabla> generar_tabla_americano(double val_monto, double val_tasa_mensual, int num_meses_plazo);

// --- Abonos extra a capital (funciones puras sobre cualquier sistema) ---
double buscar_abono_mes(const std::vector<AbonoExtra>& vec_abonos, int num_mes);
std::vector<AbonoExtra> parsear_abonos(const std::string& str_texto);
std::vector<FilaTabla> generar_tabla_frances_con_abonos(double val_monto, double val_tasa_mensual, int num_meses_plazo, const std::vector<AbonoExtra>& vec_abonos);
std::vector<FilaTabla> generar_tabla_aleman_con_abonos(double val_monto, double val_tasa_mensual, int num_meses_plazo, const std::vector<AbonoExtra>& vec_abonos);
std::vector<FilaTabla> generar_tabla_americano_con_abonos(double val_monto, double val_tasa_mensual, int num_meses_plazo, const std::vector<AbonoExtra>& vec_abonos);

// --- Utilerias de Serializacion ---
std::string serializar_tabla_json(const std::vector<FilaTabla>& vec_tabla);

#endif // AMORTIZACION_HPP
