# lexer.py
# Analizador lexico para el lenguaje QWERTY

import re

class LexerQWERTY:
    def __init__(self):
        # Palabras reservadas (codigos 1-28)
        self.palabras_reservadas = {
            'empieza': 1, 'termina': 2, 'principal': 3, 'molde': 4,
            'tiene': 5, 'haz': 6, 'crea': 7, 'da': 8, 'muestra': 9,
            'recibe': 10, 'recibe_texto': 11, 'abierto': 12, 'fijo': 13,
            'si': 14, 'sino': 15, 'mientras': 16, 'para': 17, 'hasta': 18,
            'paso': 19, 'cierto': 20, 'falso': 21, 'this': 22, 'nulo': 23,
            'salta': 24, 'sigue': 25, 'y': 26, 'o': 27, 'no': 28
        }
        
        # Tokens especiales
        self.ID_TOKEN = 100
        self.NUMERO_TOKEN = 200
        self.TEXTO_TOKEN = 300
        
        # Operadores (SIN COMA)

        self.operadores = {
        '=': 301, '<>': 302, '<': 303, '>': 304,
        '<=': 305, '>=': 306, '+': 307, '-': 308,
        '*': 309, '/': 310, '%': 311, '.': 312,
        '(': 313, ')': 314
        }
        
        self.INDENT_TOKEN = 401
        self.DEDENT_TOKEN = 402
        self.ERROR_TOKEN = 911
        self.EOF_TOKEN = 999
        
        self.errores = []
        self.tokens = []
        self.tabla_simbolos = {}
        self.nivel_actual = 0
        self.pila_indentacion = [0]
        
    def tokenizar(self, codigo):
        """Tokeniza el codigo fuente y retorna lista de tokens"""
        self.errores = []
        self.tokens = []
        self.tabla_simbolos = {}
        self.nivel_actual = 0
        self.pila_indentacion = [0]
        
        # Dividir en lineas
        lineas = codigo.split('\n')
        
        # Eliminar lineas vacias al final
        while lineas and lineas[-1].strip() == '':
            lineas.pop()
        
        # Si no hay lineas, retornar solo EOF
        if not lineas:
            self.tokens.append((self.EOF_TOKEN, '$', 'EOF', 1, 1))
            return self.tokens, self.errores
        
        # Detectar cadenas no cerradas
        cadenas_abiertas = {}
        for num, linea in enumerate(lineas, 1):
            dentro = False
            for c in linea:
                if c == '"':
                    dentro = not dentro
            if dentro:
                cadenas_abiertas[num] = True
        
        # Procesar cada linea
        for num_linea, linea_texto in enumerate(lineas, 1):
            columna_actual = 1
            
            # Verificar cadena no cerrada
            if num_linea in cadenas_abiertas:
                self.errores.append(f"Linea {num_linea}: Cadena de texto no cerrada")
                self.tokens.append((self.ERROR_TOKEN, 'ERROR_CADENA', 'CADENA_NO_CERRADA', 
                                   num_linea, columna_actual))
                continue
            
            # Calcular indentacion (en espacios)
            indentacion = self._calcular_indentacion(linea_texto)
            contenido = linea_texto.lstrip(' \t')
            
            # Procesar comentarios
            contenido = self._procesar_comentarios(contenido, num_linea)
            if contenido is None:
                continue
            
            # Procesar indentacion SOLO si hay contenido
            if contenido.strip():
                tokens_indent = self._procesar_indentacion(indentacion, num_linea)
                self.tokens.extend(tokens_indent)
                self._analizar_linea(contenido, num_linea)
        
        # Cerrar indentaciones pendientes
        while self.nivel_actual > 0:
            self.tokens.append((self.DEDENT_TOKEN, 'dedent', 'DECREMENTO_INDENTACION',
                               len(lineas), 1))
            self.nivel_actual -= 1
        
        # Agregar EOF
        self.tokens.append((self.EOF_TOKEN, '$', 'EOF', len(lineas), 1))
        
        return self.tokens, self.errores
    
    def _calcular_indentacion(self, linea):
        """Calcula el nivel de indentacion contando espacios"""
        espacios = 0
        for c in linea:
            if c == ' ':
                espacios += 1
            elif c == '\t':
                espacios += 4
            else:
                break
        return espacios
    
    def _procesar_indentacion(self, nuevo_nivel, linea_num):
        """Genera tokens INDENT/DEDENT segun el nivel"""
        tokens = []
        
        # Calcular nivel (cada 2 espacios = 1 nivel)
        if nuevo_nivel > 0:
            nivel_calculado = nuevo_nivel // 2
        else:
            nivel_calculado = 0
        
        # Si hay espacios sueltos, redondear
        if nuevo_nivel % 2 != 0 and nuevo_nivel > 0:
            nivel_calculado = (nuevo_nivel + 1) // 2
        
        if nivel_calculado > self.nivel_actual:
            if nivel_calculado - self.nivel_actual > 1:
                self.errores.append(f"Linea {linea_num}: Incremento de indentacion demasiado grande (de {self.nivel_actual} a {nivel_calculado})")
            tokens.append((self.INDENT_TOKEN, 'indent', 'INCREMENTO_INDENTACION', linea_num, 1))
            self.nivel_actual = nivel_calculado
            self.pila_indentacion.append(nivel_calculado)
        elif nivel_calculado < self.nivel_actual:
            while self.nivel_actual > nivel_calculado and len(self.pila_indentacion) > 1:
                tokens.append((self.DEDENT_TOKEN, 'dedent', 'DECREMENTO_INDENTACION', linea_num, 1))
                self.pila_indentacion.pop()
                self.nivel_actual = self.pila_indentacion[-1]
        
        return tokens
    
    def _procesar_comentarios(self, contenido, linea_num):
        """Procesa comentarios con la regla: #IDENTIFICADOR"""
        if not contenido:
            return ''
        
        pos = contenido.find('#')
        if pos == -1:
            return contenido
        
        if self._esta_dentro_cadena(contenido, pos):
            return contenido
        
        antes = contenido[:pos]
        despues = contenido[pos+1:]
        
        if not despues or despues[0] == ' ':
            self.errores.append(f"Linea {linea_num}, columna {pos+1}: # sin identificador")
            return antes.rstrip()
        
        fin_id = 0
        while fin_id < len(despues) and despues[fin_id] != ' ':
            fin_id += 1
        
        identificador = despues[:fin_id]
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identificador):
            self.errores.append(f"Linea {linea_num}, columna {pos+1}: Identificador invalido despues de #")
            return antes.rstrip()
        
        resto = despues[fin_id:]
        return (antes + resto).rstrip()
    
    def _esta_dentro_cadena(self, texto, pos):
        """Verifica si la posicion esta dentro de una cadena"""
        dentro = False
        for i, c in enumerate(texto):
            if i == pos:
                return dentro
            if c == '"':
                dentro = not dentro
        return False
    
    def _analizar_linea(self, contenido, linea_num):
        """Analiza los tokens de una linea"""
        patrones = [
            ('TEXTO_CERRADO', r'"[^"]*"'),
            ('NUMERO', r'\d+(?:\.\d+)?'),
            ('OPERADOR_DOBLE', r'[<>]=?|<>'),
            ('OPERADOR_SIMPLE', r'[+\-*/%=.()]'),
            ('IDENTIFICADOR', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('ESPACIO', r'[ \t]+'),
            ('CARACTER_INVALIDO', r'[^a-zA-Z0-9_#\"+\-*/%=.<>\s\n]')
        ]
        
        patron_general = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in patrones)
        regex = re.compile(patron_general)
        
        pos = 0
        columna_actual = 1
        asignaciones_pendientes = {}
        
        while pos < len(contenido):
            match = regex.match(contenido, pos)
            if not match:
                caracter = contenido[pos]
                self.errores.append(f"Linea {linea_num}, columna {columna_actual}: Caracter no reconocido '{caracter}'")
                self.tokens.append((self.ERROR_TOKEN, caracter, 'CARACTER_INVALIDO', linea_num, columna_actual))
                pos += 1
                columna_actual += 1
                continue
            
            tipo = match.lastgroup
            lexema = match.group()
            inicio_col = columna_actual
            columna_actual += len(lexema)
            pos = match.end()
            
            if tipo == 'ESPACIO':
                continue
            
            if tipo == 'TEXTO_CERRADO':
                self.tokens.append((self.TEXTO_TOKEN, lexema, 'LITERAL_TEXTO', linea_num, inicio_col))
                
            elif tipo == 'NUMERO':
                self.tokens.append((self.NUMERO_TOKEN, lexema, 'LITERAL_NUMERICO', linea_num, inicio_col))
                
            elif tipo in ['OPERADOR_DOBLE', 'OPERADOR_SIMPLE']:
                if lexema in self.operadores:
                    self.tokens.append((self.operadores[lexema], lexema, 'OPERADOR', linea_num, inicio_col))
                else:
                    self.errores.append(f"Linea {linea_num}, columna {inicio_col}: Operador no reconocido '{lexema}'")
                    self.tokens.append((self.ERROR_TOKEN, lexema, 'OPERADOR_INVALIDO', linea_num, inicio_col))
                    
            elif tipo == 'IDENTIFICADOR':
                if lexema in self.palabras_reservadas:
                    cod = self.palabras_reservadas[lexema]
                    if lexema in ['cierto', 'falso']:
                        self.tokens.append((cod, lexema, 'LITERAL_BOOLEANO', linea_num, inicio_col))
                    else:
                        self.tokens.append((cod, lexema, 'PALABRA_RESERVADA', linea_num, inicio_col))
                else:
                    self.tokens.append((self.ID_TOKEN, lexema, 'IDENTIFICADOR', linea_num, inicio_col))
                    if lexema not in self.tabla_simbolos:
                        self.tabla_simbolos[lexema] = {'tipo': 'Desconocido', 'linea': linea_num}
                    
                    resto = contenido[pos:].lstrip()
                    if resto and resto[0] == '=':
                        asignaciones_pendientes[lexema] = linea_num
                        
            elif tipo == 'CARACTER_INVALIDO':
                self.errores.append(f"Linea {linea_num}, columna {inicio_col}: Caracter no reconocido '{lexema}'")
                self.tokens.append((self.ERROR_TOKEN, lexema, 'CARACTER_INVALIDO', linea_num, inicio_col))
        
        # Inferir tipos de asignaciones
        for var, line in asignaciones_pendientes.items():
            if var in self.tabla_simbolos:
                for token in self.tokens:
                    if token[3] == line and token[0] in [self.NUMERO_TOKEN, self.TEXTO_TOKEN, 20, 21]:
                        if token[0] == self.NUMERO_TOKEN:
                            self.tabla_simbolos[var]['tipo'] = 'Numero'
                            self.tabla_simbolos[var]['valor'] = token[1]
                        elif token[0] == self.TEXTO_TOKEN:
                            self.tabla_simbolos[var]['tipo'] = 'Texto'
                            self.tabla_simbolos[var]['valor'] = token[1]
                        elif token[0] == 20:
                            self.tabla_simbolos[var]['tipo'] = 'Booleano'
                            self.tabla_simbolos[var]['valor'] = 'cierto'
                        elif token[0] == 21:
                            self.tabla_simbolos[var]['tipo'] = 'Booleano'
                            self.tabla_simbolos[var]['valor'] = 'falso'
                        break
    
    def get_tabla_simbolos(self):
        """Retorna la tabla de simbolos generada"""
        return self.tabla_simbolos