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

// --- Utilerias de Serializacion ---
std::string serializar_tabla_json(const std::vector<FilaTabla>& vec_tabla);

#endif // AMORTIZACION_HPP
