# parser_lr1.py
# Generador de tablas LR(1) y analizador sintactico

from collections import defaultdict


class LR1ParserGenerator:
    def __init__(self, gramatica):
        self.gramatica = gramatica
        self.producciones = gramatica['producciones']
        self.no_terminales = gramatica['no_terminales']
        self.terminales = gramatica['terminales']
        self.inicial = gramatica['inicial']
        self.nombres_terminales = gramatica.get('nombres_terminales', {})
        
        self.num_produccion = {}
        self.lista_producciones = []
        self._numerar_producciones()
        
        self.estados = []
        self.transiciones = {}
        self.accion = {}
        self.goto = {}
        self.conflictos = []
        
    def _numerar_producciones(self):
        num = 0
        for head, bodies in self.producciones.items():
            for body in bodies:
                # Si body es una lista vacía, es una producción vacía
                if not body:
                    self.num_produccion[(head, ())] = num
                    self.lista_producciones.append((head, ()))
                else:
                    self.num_produccion[(head, tuple(body))] = num
                    self.lista_producciones.append((head, tuple(body)))
                num += 1
    
    def _es_terminal(self, simbolo):
        """Verifica si un simbolo es terminal"""
        if isinstance(simbolo, int):
            return simbolo in self.terminales.values()
        return simbolo in self.terminales
    
    def _es_no_terminal(self, simbolo):
        """Verifica si un simbolo es no terminal"""
        if isinstance(simbolo, int):
            return False
        return simbolo in self.no_terminales
    
    def _first(self, simbolos):
        if not simbolos:
            return set()
        
        first = set()
        todos_tienen_epsilon = True
        
        for simbolo in simbolos:
            # Si es 'epsilon', es un terminal especial
            if simbolo == 'epsilon':
                continue
            # Si es codigo numerico, es terminal
            elif isinstance(simbolo, int):
                first.add(simbolo)
                todos_tienen_epsilon = False
                break
            elif simbolo in self.terminales:
                first.add(simbolo)
                todos_tienen_epsilon = False
                break
            elif simbolo in self.no_terminales:
                tiene_epsilon = False
                for body in self.producciones.get(simbolo, []):
                    # Si body es una lista vacía, produce epsilon
                    if not body:
                        tiene_epsilon = True
                    else:
                        first_body = self._first(tuple(body))
                        for f in first_body:
                            if f != 'epsilon':
                                first.add(f)
                        if 'epsilon' in first_body:
                            tiene_epsilon = True
                if not tiene_epsilon:
                    todos_tienen_epsilon = False
                    break
            else:
                first.add(simbolo)
                todos_tienen_epsilon = False
                break
        
        if todos_tienen_epsilon:
            first.add('epsilon')
        return first
    
    def _cerradura(self, items):
        cerradura = set(items)
        cambiado = True
        
        while cambiado:
            cambiado = False
            nuevos = set()
            
            for item in cerradura:
                head, body, dot, lookahead = item
                
                if dot < len(body):
                    simbolo = body[dot]
                    if self._es_no_terminal(simbolo):
                        beta = body[dot+1:]
                        primeros = self._first(beta + (lookahead,))
                        
                        for prod_body in self.producciones.get(simbolo, []):
                            # Si prod_body es una lista vacía, es producción vacía
                            if not prod_body:
                                prod_body_tuple = ()
                            else:
                                prod_body_tuple = tuple(prod_body)
                            
                            for terminal in primeros:
                                if terminal != 'epsilon':
                                    nuevo_item = (simbolo, prod_body_tuple, 0, terminal)
                                    if nuevo_item not in cerradura and nuevo_item not in nuevos:
                                        nuevos.add(nuevo_item)
                                        cambiado = True
                                else:
                                    nuevo_item = (simbolo, prod_body_tuple, 0, lookahead)
                                    if nuevo_item not in cerradura and nuevo_item not in nuevos:
                                        nuevos.add(nuevo_item)
                                        cambiado = True
            
            cerradura.update(nuevos)
        
        return frozenset(cerradura)
    
    def _goto(self, items, simbolo):
        nuevos_items = set()
        for item in items:
            head, body, dot, lookahead = item
            if dot < len(body) and body[dot] == simbolo:
                nuevos_items.add((head, body, dot + 1, lookahead))
        return self._cerradura(nuevos_items)
    
    def _items(self):
        inicial_aumentado = self.inicial + "'"
        eof = self.terminales['$']
        item_inicial = (inicial_aumentado, tuple(self.producciones[inicial_aumentado][0]), 0, eof)
        estado_inicial = self._cerradura({item_inicial})
        
        self.estados = [estado_inicial]
        estados_dict = {estado_inicial: 0}
        
        cambiado = True
        while cambiado:
            cambiado = False
            
            for i, estado in enumerate(self.estados):
                simbolos = set()
                for item in estado:
                    head, body, dot, lookahead = item
                    if dot < len(body):
                        simbolos.add(body[dot])
                
                for simbolo in simbolos:
                    goto_estado = self._goto(estado, simbolo)
                    if goto_estado and goto_estado not in estados_dict:
                        estados_dict[goto_estado] = len(self.estados)
                        self.estados.append(goto_estado)
                        self.transiciones[(i, simbolo)] = len(self.estados) - 1
                        cambiado = True
                    elif goto_estado:
                        self.transiciones[(i, simbolo)] = estados_dict[goto_estado]
        
        return self.estados
    
    def _construir_tablas(self):
        self._items()
        
        self.accion = defaultdict(dict)
        self.goto = defaultdict(dict)
        self.conflictos = []
        
        for i, estado in enumerate(self.estados):
            for item in estado:
                head, body, dot, lookahead = item
                
                if dot < len(body):
                    simbolo = body[dot]
                    if self._es_terminal(simbolo):
                        if (i, simbolo) in self.transiciones:
                            j = self.transiciones[(i, simbolo)]
                            if simbolo in self.accion[i]:
                                if self.accion[i][simbolo][0] == 'reducir':
                                    self.conflictos.append((i, simbolo, 'shift-reduce'))
                            self.accion[i][simbolo] = ('desplazar', j)
                    elif self._es_no_terminal(simbolo):
                        if (i, simbolo) in self.transiciones:
                            j = self.transiciones[(i, simbolo)]
                            self.goto[i][simbolo] = j
                else:
                    if head == self.inicial + "'":
                        self.accion[i][self.terminales['$']] = ('aceptar',)
                    else:
                        num_prod = self.num_produccion.get((head, body))
                        if num_prod is not None:
                            if lookahead in self.accion[i]:
                                if self.accion[i][lookahead][0] == 'reducir':
                                    self.conflictos.append((i, lookahead, 'reduce-reduce'))
                                elif self.accion[i][lookahead][0] == 'desplazar':
                                    self.conflictos.append((i, lookahead, 'shift-reduce'))
                            self.accion[i][lookahead] = ('reducir', num_prod)
        
        # Resolver conflictos: shift > reduce
        for estado, simbolo, tipo in self.conflictos:
            if tipo == 'shift-reduce' and simbolo in self.accion[estado]:
                acciones = self.accion[estado][simbolo]
                if isinstance(acciones, list):
                    nuevas_acciones = [a for a in acciones if a[0] == 'desplazar']
                    if nuevas_acciones:
                        self.accion[estado][simbolo] = nuevas_acciones[0]
                    else:
                        self.accion[estado][simbolo] = acciones[0]
        
        self.accion = dict(self.accion)
        self.goto = dict(self.goto)
    
    def generar_parser(self):
        self._construir_tablas()
        return LR1Parser(self)
    
    def get_estados(self):
        return self.estados
    
    def get_conflictos(self):
        return self.conflictos


class LR1Parser:
    def __init__(self, generador):
        self.generador = generador
        self.accion = generador.accion
        self.goto = generador.goto
        self.lista_producciones = generador.lista_producciones
        self.estados = generador.estados
        self.terminales = generador.terminales
        self.no_terminales = generador.no_terminales
        self.nombres_terminales = generador.nombres_terminales
        
        self.pila = []
        self.pila_simbolos = []
        self.tokens = []
        self.pos = 0
        self.errores = []
        self.errores_omitidos = 0
        self.pasos = []
        self.shifts = 0
        self.reduces = 0
        self.aceptado = False
        
        # Abreviaturas de los no terminales, solo para que la traza
        # (Pila de simbolos / Accion) se vea compacta en la terminal.
        # No afecta la gramatica ni el analisis, es unicamente visual.
        self.abreviaturas_simbolos = {
            "S'": "S'", 'S': 'S',
            'Programa': 'Prog',
            'BloquePrincipal': 'BPrincipal',
            'ListaDeclaracionesGlobales': 'LDG',
            'DeclaracionGlobal': 'DG',
            'DeclConstante': 'DConst',
            'DeclVariableGlobal': 'DVarG',
            'DeclClase': 'DClase',
            'DeclMetodoOProcGlobal': 'DMetProcG',
            'CuerpoClase': 'CClase',
            'ListaAtributos': 'LAtrib',
            'Atributo': 'Atrib',
            'ListaMetodos': 'LMet',
            'MetodoOProc': 'MetProc',
            'Parametros': 'Params',
            'ListaParams': 'LParams',
            'Param': 'Param',
            'CuerpoFuncProc': 'CFuncProc',
            'ListaInstrucciones': 'LInst',
            'Instruccion': 'Inst',
            'Asignacion': 'Asig',
            'Condicional': 'Cond',
            'Sino': 'Sino',
            'BucleMientras': 'BMientras',
            'BuclePara': 'BPara',
            'Paso': 'Paso',
            'EntradaSalida': 'ES',
            'Bifurcacion': 'Bif',
            'RetornoFuncion': 'RetF',
            'RetornoProc': 'RetP',
            'LlamadaMetodo': 'LlamMet',
            'ListaArgumentos': 'LArg',
            'Argumentos': 'Args',
            'Argumento': 'Arg',
            'Expresion': 'E',
            'E': 'E',
            'ETermino': 'ET',
            'T': 'T',
            'TTermino': 'TT',
            'F': 'F',
            'Comparacion': 'Comp',
            'ComparacionOp': 'CompOp',
            'Relacional': 'Rel',
            'RelacionalTermino': 'RelT',
            'LogicoY': 'LogY',
            'LogicoYTermino': 'LogYT',
            'LogicoO': 'LogO',
            'LogicoOTermino': 'LogOT',
        }
        
    def _abrev(self, simbolo):
        """Version abreviada de un simbolo (solo para mostrar en pantalla)."""
        if isinstance(simbolo, str):
            return self.abreviaturas_simbolos.get(simbolo, simbolo)
        return simbolo
        
    def parse(self, tokens, mostrar_traza=True):
        self.tokens = tokens
        self.pos = 0
        self.pila = [0]
        self.pila_simbolos = []
        self.errores = []
        self.errores_omitidos = 0
        self.pasos = []
        self.shifts = 0
        self.reduces = 0
        self.aceptado = False
        
        paso = 1
        max_errores = 5
        
        if tokens:
            print(f"\n[DEBUG PARSER] Primer token: {tokens[0]}")
            print(f"[DEBUG PARSER] Codigo esperado para 'empieza' en gramatica: {self.terminales.get('empieza')}")
        
        while True:
            estado = self.pila[-1]
            token_actual = self._token_actual()
            
            if not token_actual:
                simbolo = self.terminales['$']
                lexema = '$'
                linea = '?'
                codigo_token = self.terminales['$']
            else:
                simbolo = token_actual[0]
                lexema = token_actual[1]
                linea = token_actual[3]
                codigo_token = token_actual[0]
            
            if paso == 1:
                print(f"[DEBUG PARSER] Paso 1: Estado={estado}, Codigo_token={codigo_token}, Lexema='{lexema}'")
                print(f"[DEBUG PARSER] Acciones en estado {estado}: {list(self.accion.get(estado, {}).keys())}")
                print(f"[DEBUG PARSER] ¿Coincide codigo? {codigo_token in self.accion.get(estado, {})}")
            
            accion = None
            if estado in self.accion and simbolo in self.accion[estado]:
                accion = self.accion[estado][simbolo]
            
            if mostrar_traza and paso <= 50:
                self._registrar_paso(paso, estado, token_actual, accion)
            
            if accion is None:
                if len(self.errores) >= max_errores:
                    print(f"\n[ERROR] Demasiados errores ({max_errores}). Deteniendo.")
                    print(f"[DEBUG] Ultimo estado: {estado}, simbolo: '{lexema}', codigo: {codigo_token}")
                    if estado in self.accion:
                        print(f"[DEBUG] Acciones disponibles: {list(self.accion[estado].keys())}")
                    if mostrar_traza:
                        self._imprimir_tabla_traza()
                    return False, self.errores, self.pasos
                
                if simbolo == '$':
                    esperado = self._obtener_esperados()
                    self.errores.append(
                        f"[ERROR] en EOF: se esperaba {esperado}, pero la entrada termino"
                    )
                    print(f"  [ERROR] en EOF: se esperaba {esperado}, pero la entrada termino")
                    if mostrar_traza:
                        self._imprimir_tabla_traza()
                    return False, self.errores, self.pasos
                else:
                    self._recuperar_error(token_actual)
                    paso += 1
                    continue
            
            if accion[0] == 'desplazar':
                _, nuevo_estado = accion
                self.pila_simbolos.append(token_actual)
                self.pila.append(nuevo_estado)
                self.pos += 1
                self.shifts += 1
                
            elif accion[0] == 'reducir':
                _, num_produccion = accion
                head, body = self.lista_producciones[num_produccion]
                
                if paso <= 15:
                    head_abrev = self._abrev(head)
                    if body:
                        body_str = ' '.join(self._abrev(b) if isinstance(b, str) else str(b) for b in body)
                        print(f"[DEBUG] Reduciendo: {head_abrev} -> {body_str}")
                    else:
                        print(f"[DEBUG] Reduciendo: {head_abrev} -> epsilon")
                
                # Pop elementos de la pila
                for _ in range(len(body)):
                    if self.pila:
                        self.pila.pop()
                    if self.pila_simbolos:
                        self.pila_simbolos.pop()
                
                estado_actual = self.pila[-1]
                
                if estado_actual in self.goto and head in self.goto[estado_actual]:
                    nuevo_estado = self.goto[estado_actual][head]
                    self.pila_simbolos.append(head)
                    self.pila.append(nuevo_estado)
                    self.reduces += 1
                else:
                    self.errores.append(f"Error: No hay goto para {head} desde estado {estado_actual}")
                    if mostrar_traza:
                        print(f"  [ERROR] No hay goto para {head} desde estado {estado_actual}")
                    self._recuperar_error(token_actual)
                    
            elif accion[0] == 'aceptar':
                self.aceptado = True
                if mostrar_traza:
                    self._imprimir_tabla_traza()
                    print("  [ACEPTADO]")
                return True, self.errores, self.pasos
            
            paso += 1
            
            if paso > 500:
                print("[ERROR] Limite de pasos excedido (500)")
                if mostrar_traza:
                    self._imprimir_tabla_traza()
                return False, self.errores, self.pasos
        
        return False, self.errores, self.pasos
    
    def _token_actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def _token_texto(self, token):
        if token:
            return token[1]
        return 'EOF'
    
    def _token_linea(self, token):
        if token:
            return token[3]
        return '?'
    
    def _registrar_paso(self, paso, estado, token, accion):
        """Calcula los datos de un paso y los guarda en self.pasos.
        Ya no imprime nada aqui: la tabla completa se imprime al final,
        con _imprimir_tabla_traza(), para que las columnas se calculen
        segun el contenido real (sin cortar nada)."""
        pila_estados = ' '.join(str(s) for s in self.pila[-10:])
        pila_simb = ' '.join(t[1] if isinstance(t, tuple) else self._abrev(t) for t in self.pila_simbolos[-10:])
        entrada = ' '.join(t[1] for t in self.tokens[self.pos:self.pos+10]) if self.pos < len(self.tokens) else '$'
        
        if accion is None:
            accion_str = '[ERROR]'
        elif accion[0] == 'desplazar':
            accion_str = f"Desplazar a estado {accion[1]}"
        elif accion[0] == 'reducir':
            head, body = self.lista_producciones[accion[1]]
            head_abrev = self._abrev(head)
            if body:
                body_str = ' '.join(self._abrev(b) if isinstance(b, str) else str(b) for b in body)
                accion_str = f"Reducir {head_abrev} -> {body_str}"
            else:
                accion_str = f"Reducir {head_abrev} -> epsilon"
        elif accion[0] == 'aceptar':
            accion_str = 'Aceptar'
        else:
            accion_str = str(accion)
        
        self.pasos.append((paso, pila_estados, pila_simb, entrada, accion_str))
    
    def _imprimir_tabla_traza(self):
        """Imprime self.pasos como una tabla bien cuadrada, SIN cortar
        contenido: el ancho de cada columna se calcula con el valor mas
        largo que realmente aparece en ella (incluyendo el encabezado)."""
        encabezados = ['Paso', 'Pila(estados)', 'Pila(simbolos)', 'Entrada', 'Accion']
        
        if not self.pasos:
            return
        
        filas = [[str(valor) for valor in fila] for fila in self.pasos]
        
        anchos = [len(h) for h in encabezados]
        for fila in filas:
            for i, valor in enumerate(fila):
                anchos[i] = max(anchos[i], len(valor))
        
        def _fila(valores):
            celdas = [valores[i].ljust(anchos[i]) for i in range(len(valores))]
            return '| ' + ' | '.join(celdas) + ' |'
        
        linea_encabezado = _fila(encabezados)
        separador = '-' * len(linea_encabezado)
        
        print(separador)
        print(linea_encabezado)
        print(separador)
        for fila in filas:
            print(_fila(fila))
        print(separador)
    
    def _recuperar_error(self, token):
        puntos_sincro = [1, 2, 3, 4, 6, 14, 15, 16, 17, 24, 25, 999]
        
        if token:
            linea = self._token_linea(token)
            lexema = self._token_texto(token)
            esperado = self._obtener_esperados()
            
            self.errores.append(
                f"[ERROR] en linea {linea}: se encontro '{lexema}', se esperaba {esperado}"
            )
            print(f"  [ERROR] en linea {linea}: se encontro '{lexema}', se esperaba {esperado}")
        else:
            self.errores.append("[ERROR] en EOF: entrada incompleta")
            print("  [ERROR] en EOF: entrada incompleta")
            return
        
        tokens_saltados = 0
        while self.pos < len(self.tokens):
            token_actual = self.tokens[self.pos]
            if token_actual[0] in puntos_sincro:
                break
            self.pos += 1
            tokens_saltados += 1
        
        if tokens_saltados > 0:
            print(f"  [Recuperando... saltando {tokens_saltados} token(s) hasta sincronizar]")
            self.errores.append(f"  Se omitieron {tokens_saltados} tokens hasta recuperar")
            self.errores_omitidos += tokens_saltados
        
        self.pila = [0]
        self.pila_simbolos = []
        
        if self.pos < len(self.tokens):
            token_actual = self.tokens[self.pos]
            if token_actual[0] in puntos_sincro and token_actual[0] != 999:
                self.pos += 1
                print(f"  [Sincronizado en token '{token_actual[1]}']")
    
    def _obtener_esperados(self):
        estado = self.pila[-1]
        esperados = []
        
        if estado in self.accion:
            for simbolo, accion in self.accion[estado].items():
                if accion[0] == 'desplazar' or accion[0] == 'reducir':
                    if isinstance(simbolo, int):
                        if simbolo in self.nombres_terminales:
                            esperados.append(self.nombres_terminales[simbolo])
                        else:
                            esperados.append(str(simbolo))
                    else:
                        esperados.append(str(simbolo))
        
        if esperados:
            if len(esperados) > 5:
                return ', '.join(esperados[:5]) + ', ...'
            return ', '.join(esperados)
        return 'algun token valido'
    
    def get_stats(self):
        return {
            'shifts': self.shifts,
            'reduces': self.reduces,
            'errores': len(self.errores),
            'errores_omitidos': self.errores_omitidos,
            'pasos': len(self.pasos),
            'aceptado': self.aceptado
        }