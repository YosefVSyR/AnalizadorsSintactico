# main.py
# Programa principal - Analizador Sintactico LR(1) para QWERTY

import time
from lexer import LexerQWERTY
from parser_lr1 import LR1ParserGenerator, encabezado_traza, separador_traza
from gramatica import crear_gramatica_qwerty


def leer_codigo():
    """
    Lee el codigo QWERTY desde la entrada estandar.
    Para finalizar, escriba '---' en una linea vacia.
    """
    print("-" * 70)
    print("Ingrese el codigo QWERTY (escriba '---' en una linea vacia para analizar):")
    print("-" * 70)
    
    lineas = []
    
    while True:
        try:
            linea = input()
            # Si la linea es '---', finalizar
            if linea.strip() == '---':
                break
            # Si la linea es 'EOF' (por compatibilidad)
            if linea.strip() == 'EOF':
                break
            lineas.append(linea)
        except EOFError:
            # Ctrl+D o Ctrl+Z
            break
        except KeyboardInterrupt:
            print("\n\nInterrupcion detectada. Saliendo...")
            return []
    
    # Si no hay lineas, retornar vacio
    if not lineas:
        return []
    
    # DEBUG: Mostrar las lineas leidas
    print(f"\n[DEBUG] Lineas leidas: {len(lineas)}")
    if lineas:
        print(f"[DEBUG] Primera linea: '{repr(lineas[0])}'")
        print(f"[DEBUG] Ultima linea: '{repr(lineas[-1])}'")
    
    return lineas


def mostrar_tokens(tokens, max_mostrar=30):
    """Muestra los tokens generados"""
    print("\n[TOKENS GENERADOS]")
    print("  #   | CODIGO | CATEGORIA              | LEXEMA | LINEA | COLUMNA")
    print("  ----|--------|------------------------|--------|-------|--------")
    for i, token in enumerate(tokens[:max_mostrar]):
        cod, lex, cat, linea, col = token
        print(f"  {i+1:3d} | {cod:6d} | {cat:22s} | '{lex}' |  {linea:3d}  |  {col:3d}")
    if len(tokens) > max_mostrar:
        print(f"  ... y {len(tokens)-max_mostrar} tokens mas")
    print(f"  Total: {len(tokens)} tokens")


def mostrar_resumen(parser, errores_lexicos, elapsed, tokens):
    """Muestra el resumen del analisis"""
    stats = parser.get_stats()
    total_errores = len(errores_lexicos) + stats['errores']
    
    print("\n" + "=" * 70)
    print("RESUMEN")
    print("=" * 70)
    print(f"  Tokens: {len(tokens)}")
    print(f"  Shifts: {stats['shifts']} | Reduces: {stats['reduces']} | "
          f"Tiempo: {elapsed:.4f}s | Errores: {total_errores}")
    
    if total_errores > 0:
        print("\n  ERRORES ENCONTRADOS:")
        todos_errores = []
        if errores_lexicos:
            todos_errores.extend(errores_lexicos)
        if parser.errores:
            todos_errores.extend(parser.errores)
        
        for i, error in enumerate(todos_errores, 1):
            print(f"    {i}. {error}")
        print(f"\n[ANALISIS COMPLETADO CON {total_errores} ERRORES]")
    else:
        print("\n[ACEPTADO] La cadena pertenece al lenguaje QWERTY")


def main():
    print("=" * 70)
    print("  ANALIZADOR SINTACTICO LR(1) - LENGUAJE QWERTY")
    print("  Instrucciones: Escriba el codigo y luego '---' en una linea vacia")
    print("  (Tambien puede usar 'EOF' o Ctrl+D/Ctrl+Z)")
    print("=" * 70)
    
    # Cargar gramatica
    print("\n[Cargando gramatica...]")
    gramatica = crear_gramatica_qwerty()
    
    print("[Generando tablas LR(1)...]")
    generador = LR1ParserGenerator(gramatica)
    parser = generador.generar_parser()
    
    print(f"  Estados: {len(generador.get_estados())}")
    print(f"  Producciones: {sum(len(v) for v in gramatica['producciones'].values())}")
    
    conflictos = generador.get_conflictos()
    if conflictos:
        print(f"  [INFO] {len(conflictos)} conflictos resueltos")
    
    # ============================================================
    # DEBUG: VERIFICAR CODIGOS DE TERMINALES
    # ============================================================
    lexer = LexerQWERTY()
    
    print("\n" + "=" * 70)
    print("[DEBUG] VERIFICACION DE CODIGOS DE TERMINALES")
    print("=" * 70)
    
    # Verificar codigo de 'empieza'
    codigo_gramatica = gramatica['terminales'].get('empieza')
    codigo_lexer = lexer.palabras_reservadas.get('empieza')
    
    print(f"  Codigo de 'empieza' en gramatica: {codigo_gramatica}")
    print(f"  Codigo de 'empieza' en lexer:     {codigo_lexer}")
    
    if codigo_gramatica == codigo_lexer:
        print("  [OK] Los codigos coinciden")
    else:
        print("  [ERROR] Los codigos NO coinciden!")
        print("  Esto causa que el parser no reconozca el token 'empieza'")
        print("  Asegurese de que ambos archivos tengan los mismos codigos")
    
    # Verificar codigo de 'principal'
    codigo_gramatica = gramatica['terminales'].get('principal')
    codigo_lexer = lexer.palabras_reservadas.get('principal')
    
    print(f"  Codigo de 'principal' en gramatica: {codigo_gramatica}")
    print(f"  Codigo de 'principal' en lexer:     {codigo_lexer}")
    
    if codigo_gramatica == codigo_lexer:
        print("  [OK] Los codigos coinciden")
    else:
        print("  [ERROR] Los codigos NO coinciden!")
    
    # Verificar codigo de 'termina'
    codigo_gramatica = gramatica['terminales'].get('termina')
    codigo_lexer = lexer.palabras_reservadas.get('termina')
    
    print(f"  Codigo de 'termina' en gramatica: {codigo_gramatica}")
    print(f"  Codigo de 'termina' en lexer:     {codigo_lexer}")
    
    if codigo_gramatica == codigo_lexer:
        print("  [OK] Los codigos coinciden")
    else:
        print("  [ERROR] Los codigos NO coinciden!")
    
    print("=" * 70)
    # ============================================================
    
    # Bucle principal
    while True:
        lineas = leer_codigo()
        
        if not lineas:
            print("\nSaliendo del programa...")
            break
        
        codigo = '\n'.join(lineas)
        
        print("\n" + "=" * 70)
        print("ENTRADA:")
        print("=" * 70)
        print(codigo)
        print("-" * 70)
        
        # Mostrar el codigo con caracteres especiales para depurar
        print("[DEBUG] Codigo en bytes:")
        print(repr(codigo))
        print("-" * 70)
        
        start_time = time.time()
        tokens, errores_lexicos = lexer.tokenizar(codigo)
        
        mostrar_tokens(tokens)
        
        if errores_lexicos:
            print("\n[ERRORES LEXICOS]")
            for error in errores_lexicos:
                print(f"  {error}")
        
        if len(tokens) <= 1:
            print("\n[ERROR] No se generaron tokens. Verifique el codigo ingresado.")
            print("  Asegurese de que la primera linea sea 'empieza' sin espacios.")
            continue
        
        print("\n" + "=" * 70)
        print("ANALISIS SINTACTICO LR(1)")
        print("=" * 70)
        print(encabezado_traza())
        print(separador_traza())
        
        parser.parse(tokens, mostrar_traza=True)
        
        print(separador_traza())
        
        elapsed = time.time() - start_time
        
        mostrar_resumen(parser, errores_lexicos, elapsed, tokens)


if __name__ == "__main__":
    main()