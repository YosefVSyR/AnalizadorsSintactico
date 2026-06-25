# gramatica.py
# Definicion de la gramatica del lenguaje QWERTY

def crear_gramatica_qwerty():
    """
    Crea la gramatica del lenguaje QWERTY para LR(1)
    """
    
    # TERMINALES
    terminales = {
        'empieza': 1, 'termina': 2, 'principal': 3, 'molde': 4,
        'tiene': 5, 'haz': 6, 'crea': 7, 'da': 8, 'muestra': 9,
        'recibe': 10, 'recibe_texto': 11, 'abierto': 12, 'fijo': 13,
        'si': 14, 'sino': 15, 'mientras': 16, 'para': 17, 'hasta': 18,
        'paso': 19, 'cierto': 20, 'falso': 21, 'this': 22, 'nulo': 23,
        'salta': 24, 'sigue': 25, 'y': 26, 'o': 27, 'no': 28,
        'ID': 100, 'NUMERO': 200, 'TEXTO': 300,
        '=': 301, '<>': 302, '<': 303, '>': 304,
        '<=': 305, '>=': 306, '+': 307, '-': 308,
        '*': 309, '/': 310, '%': 311, '.': 312,
        '(': 313, ')': 314,
        'indent': 401, 'dedent': 402, '$': 999
    }
    
    nombres_terminales = {v: k for k, v in terminales.items()}
    
    no_terminales = [
        'Programa', 'BloquePrincipal', 'ListaDeclaracionesGlobales',
        'DeclaracionGlobal', 'DeclConstante', 'DeclVariableGlobal',
        'DeclClase', 'DeclMetodoOProcGlobal', 'CuerpoClase',
        'ListaAtributos', 'Atributo', 'ListaMetodos', 'MetodoOProc',
        'Parametros', 'ListaParams', 'Param', 'CuerpoFuncProc',
        'ListaInstrucciones', 'Instruccion', 'Asignacion',
        'Condicional', 'Sino', 'BucleMientras', 'BuclePara',
        'Paso', 'EntradaSalida', 'Bifurcacion', 'RetornoFuncion',
        'RetornoProc', 'LlamadaMetodo', 'ListaArgumentos',
        'Argumentos', 'Argumento', 'Expresion', 'E', 'ETermino', 'T', 'TTermino', 'F',
        'Comparacion', 'ComparacionOp', 'Relacional',
        'RelacionalTermino', 'LogicoY', 'LogicoYTermino',
        'LogicoO', 'LogicoOTermino'
    ]
    
    t = terminales
    cod = {
        'empieza': t['empieza'],
        'termina': t['termina'],
        'principal': t['principal'],
        'molde': t['molde'],
        'tiene': t['tiene'],
        'haz': t['haz'],
        'crea': t['crea'],
        'da': t['da'],
        'muestra': t['muestra'],
        'recibe': t['recibe'],
        'recibe_texto': t['recibe_texto'],
        'abierto': t['abierto'],
        'fijo': t['fijo'],
        'si': t['si'],
        'sino': t['sino'],
        'mientras': t['mientras'],
        'para': t['para'],
        'hasta': t['hasta'],
        'paso': t['paso'],
        'cierto': t['cierto'],
        'falso': t['falso'],
        'this': t['this'],
        'nulo': t['nulo'],
        'salta': t['salta'],
        'sigue': t['sigue'],
        'y': t['y'],
        'o': t['o'],
        'no': t['no'],
        'ID': t['ID'],
        'NUMERO': t['NUMERO'],
        'TEXTO': t['TEXTO'],
        '=': t['='],
        '<>': t['<>'],
        '<': t['<'],
        '>': t['>'],
        '<=': t['<='],
        '>=': t['>='],
        '+': t['+'],
        '-': t['-'],
        '*': t['*'],
        '/': t['/'],
        '%': t['%'],
        '.': t['.'],
        '(': t['('],
        ')': t[')'],
        'indent': t['indent'],
        'dedent': t['dedent'],
        '$': t['$']
    }
    
    producciones = {
        'S': [[cod['empieza'], 'Programa', cod['termina']]],
        'Programa': [['ListaDeclaracionesGlobales', 'BloquePrincipal']],
        'ListaDeclaracionesGlobales': [['DeclaracionGlobal', 'ListaDeclaracionesGlobales'], []],
        'DeclaracionGlobal': [
            ['DeclConstante'], ['DeclVariableGlobal'], 
            ['DeclClase'], ['DeclMetodoOProcGlobal']
        ],
        'DeclConstante': [[cod['fijo'], cod['ID'], cod['='], 'Expresion']],
        'DeclVariableGlobal': [
            [cod['abierto'], cod['ID'], cod['='], 'Expresion'],
            [cod['ID'], cod['='], 'Expresion']
        ],
        'DeclClase': [[cod['molde'], cod['ID'], cod['indent'], 'ListaAtributos', 'ListaMetodos', cod['dedent']]],
        'DeclMetodoOProcGlobal': [
            [cod['haz'], cod['ID'], 'Parametros', cod['indent'], 'CuerpoFuncProc', cod['dedent']]
        ],
        'ListaAtributos': [['Atributo', 'ListaAtributos'], []],
        'Atributo': [
            [cod['tiene'], cod['ID'], cod['='], 'Expresion'],
            [cod['tiene'], cod['ID']]
        ],
        'ListaMetodos': [['MetodoOProc', 'ListaMetodos'], []],
        'MetodoOProc': [
            [cod['haz'], cod['ID'], 'Parametros', cod['indent'], 'CuerpoFuncProc', cod['dedent']]
        ],
        'Parametros': [['ListaParams'], []],
        'ListaParams': [['Param', 'ListaParams'], ['Param']],
        'Param': [[cod['ID']]],
        'CuerpoFuncProc': [
            ['ListaInstrucciones', 'RetornoFuncion'],
            ['ListaInstrucciones', 'RetornoProc'],
            ['ListaInstrucciones']
        ],
        'BloquePrincipal': [[cod['principal'], cod['indent'], 'ListaInstrucciones', cod['dedent']]],
        'ListaInstrucciones': [['Instruccion', 'ListaInstrucciones'], []],
        'Instruccion': [
            ['Asignacion'], ['Condicional'], ['BucleMientras'], ['BuclePara'],
            ['EntradaSalida'], ['Bifurcacion'], ['LlamadaMetodo'],
            ['RetornoFuncion'], ['RetornoProc']
        ],
        'Asignacion': [
            [cod['ID'], cod['='], 'Expresion'],
            [cod['ID'], cod['.'], cod['ID'], cod['='], 'Expresion']
        ],
        'Condicional': [[cod['si'], 'Expresion', cod['indent'], 'ListaInstrucciones', cod['dedent'], 'Sino']],
        'Sino': [
            [cod['sino'], cod['indent'], 'ListaInstrucciones', cod['dedent']],
            [cod['sino'], cod['si'], 'Expresion', cod['indent'], 'ListaInstrucciones', cod['dedent'], 'Sino'],
            []
        ],
        'BucleMientras': [[cod['mientras'], 'Expresion', cod['indent'], 'ListaInstrucciones', cod['dedent']]],
        'BuclePara': [
            [cod['para'], cod['ID'], cod['='], 'Expresion', cod['hasta'], 'Expresion', 'Paso', 
             cod['indent'], 'ListaInstrucciones', cod['dedent']]
        ],
        'Paso': [[cod['paso'], 'Expresion'], []],
        'EntradaSalida': [
            [cod['muestra'], 'Expresion'],
            [cod['recibe'], cod['ID']],
            [cod['recibe_texto'], cod['ID']]
        ],
        'Bifurcacion': [[cod['salta']], [cod['sigue']]],
        'RetornoFuncion': [[cod['da'], 'Expresion']],
        'RetornoProc': [[cod['da']]],
        'LlamadaMetodo': [
            [cod['ID'], cod['.'], cod['ID'], 'Argumentos'],
            [cod['crea'], cod['ID']]
        ],
        'ListaArgumentos': [['Argumentos'], []],
        'Argumentos': [['Argumento', 'Argumentos'], ['Argumento']],
        'Argumento': [['Expresion']],
        
        # ============================================================
        # EXPRESIONES - CON RECURSION IZQUIERDA MANEJADA CON TERMINOS
        # ============================================================
        
        'Expresion': [['LogicoO']],
        
        'LogicoO': [['LogicoY', 'LogicoOTermino']],
        'LogicoOTermino': [
            [cod['o'], 'LogicoY', 'LogicoOTermino'],
            []
        ],
        
        'LogicoY': [['Comparacion', 'LogicoYTermino']],
        'LogicoYTermino': [
            [cod['y'], 'Comparacion', 'LogicoYTermino'],
            []
        ],
        
        'Comparacion': [['E', 'ComparacionOp']],
        'ComparacionOp': [
            ['Relacional', 'RelacionalTermino'],
            []
        ],
        
        'Relacional': [
            [cod['=']], [cod['<>']], [cod['<']], [cod['>']], [cod['<=']], [cod['>=']]
        ],
        
        'RelacionalTermino': [
            ['Relacional', 'E', 'RelacionalTermino'],
            []
        ],
        
        'E': [['T', 'ETermino']],
        'ETermino': [
            [cod['+'], 'T', 'ETermino'],
            [cod['-'], 'T', 'ETermino'],
            []
        ],
        
        'T': [['F', 'TTermino']],
        'TTermino': [
            [cod['*'], 'F', 'TTermino'],
            [cod['/'], 'F', 'TTermino'],
            [cod['%'], 'F', 'TTermino'],
            []
        ],
        
        'F': [
            [cod['ID']], [cod['NUMERO']], [cod['TEXTO']], [cod['cierto']], [cod['falso']],
            [cod['nulo']], [cod['this']], 
            [cod['ID'], cod['.'], cod['ID']],
            [cod['('], 'Expresion', cod[')']], 
            [cod['no'], 'F'], 
            [cod['-'], 'F']
        ]
    }
    
    # AUMENTAR GRAMATICA (S' -> S)
    producciones_aumentadas = producciones.copy()
    simbolo_inicial = 'S'
    producciones_aumentadas[simbolo_inicial + "'"] = [[simbolo_inicial]]
    
    no_terminales_aumentados = [simbolo_inicial + "'", simbolo_inicial] + no_terminales
    
    return {
        'producciones': producciones_aumentadas,
        'no_terminales': no_terminales_aumentados,
        'terminales': terminales,
        'inicial': simbolo_inicial,
        'nombres_terminales': nombres_terminales
    }