import unittest
from minimal_compiler.src.generator.template_loader import set_path_explicitly
from util import compile_and_run

class TestPrograms(unittest.TestCase):
    def __init__(self, methodName = "runTest"):
        super().__init__(methodName)

        set_path_explicitly("../../minimal_compiler/src/generator/templates/")

    def test_age_check(self):
        code = """
            /*
            Ein kleines Beispielprogramm, welches die Kontrollsruktur "if-else" demonstriert.
            Dabei kann der Benutzer sein Alter in n1 eingeben und das Programm gibt die Altersklasse aus.

            Altersklassen:
            - 0-17: Kind (0)
                - Wenn das Kind unter 6 ist dann ist es ein Kleinkind
            - 18-64: Erwachsener (1)
            - 65+: Senior (2)

            */

            let alter, alterklasse, achtungDringendElternBenachrichtigen;

            alter = x1; // Alter direkt von der Eingabe
            achtungDringendElternBenachrichtigen = 0;

            if alter > 18 then
                if alter > 64 then
                    alterklasse = 2 // Senior
                else
                    alterklasse = 1 // Erwachsener
                end
            else
                if 6 > alter then
                    achtungDringendElternBenachrichtigen = 1000
                end;

                alterklasse = 0 // Kind
            end;

            // in Ausgabe schreiben
            if achtungDringendElternBenachrichtigen == 0 then 
                x0 = alterklasse
            else
                x0 = achtungDringendElternBenachrichtigen
            end
        """
        args1 = {"n1": 100}
        args2 = {"n1": 1}
        args3 = {"n1": 42}
        args4 = {"n1": 18}

        expected_result1 = 2 
        expected_result2 = 1000
        expected_result3 = 1 
        expected_result4 = 0

        results = compile_and_run(code, "test_age_check", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")

    def test_fib(self):
        code = """
            /*

            Beispiel Programm, welches die Fibonacci-Zahlen iterativ berechnet.

            Die Input-Variable n1 gibt die Anzahl der Fibonacci-Zahlen an, die berechnet werden sollen.
            Als Output wird die n-te Fibonacci-Zahl ausgegeben.

            */

            let n, a, b, i;
            n = x1; // Anzahl der Fibonacci-Zahlen

            a = 0;
            b = 1;
            i = 2;
            while n > i do
                let c;
                c = a + b;
                a = b;
                b = c;
                i = i + 1
            end;

            x0 = b
        """
        args1 = {"n1": 5}
        args2 = {"n1": 11}
        args3 = {"n1": 10}
        args4 = {"n1": 10000}

        expected_result1 = 3
        expected_result2 = 55
        expected_result3 = 34
        expected_result4 = 20793608237133498072112648988642836825087036094015903119682945866528501423455686648927456034305226515591757343297190158010624794267250973176133810179902738038231789748346235556483191431591924532394420028067810320408724414693462849062668387083308048250920654493340878733226377580847446324873797603734794648258113858631550404081017260381202919943892370942852601647398213554479081823593715429566945149312993664846779090437799284773675379284270660175134664833266377698642012106891355791141872776934080803504956794094648292880566056364718187662668970758537383352677420835574155945658542003634765324541006121012446785689171494803262408602693091211601973938229446636049901531963286159699077880427720289235539329671877182915643419079186525118678856821600897520171070499437657067342400871083908811800976259727431820539554256869460815355918458253398234382360435762759823179896116748424269545924633204614137992850814352018738480923581553988990897151469406131695614497783720743461373756218685106856826090696339815490921253714537241866911604250597353747823733268178182198509240226955826416016690084749816072843582488613184829905383150180047844353751554201573833105521980998123833253261228689824051777846588461079790807828367132384798451794011076569057522158680378961532160858387223882974380483931929541222100800313580688585002598879566463221427820448492565073106595808837401648996423563386109782045634122467872921845606409174360635618216883812562321664442822952537577492715365321134204530686742435454505103269768144370118494906390254934942358904031509877369722437053383165360388595116980245927935225901537634925654872380877183008301074569444002426436414756905094535072804764684492105680024739914490555904391369218696387092918189246157103450387050229300603241611410707453960080170928277951834763216705242485820801423866526633816082921442883095463259080471819329201710147828025221385656340207489796317663278872207607791034431700112753558813478888727503825389066823098683355695718137867882982111710796422706778536913192342733364556727928018953989153106047379741280794091639429908796650294603536651238230626

        results = compile_and_run(code, "test_fib", [args1, args2, args3, args4])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]
        result4 = results[3]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args2} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")
        self.assertEqual(result4, expected_result4, f"Test case with {args4} failed, expected {expected_result4}, got {result4}")

    def test_self_compiler_lexer_bug(self):
        code = """
            let wordLen, foundNum, num, mult, shift, word, digit;

            x1 = 219885614456;
            x2 = 5;

            let lol;
            lol = 4;
            while lol > 0 do
                wordLen = 1;
                foundNum = 1;
                num = 0;
                mult = 10;
                while foundNum > 0 do
                    foundNum = 0;
                    shift = x2 - wordLen;
                    shift = shift * 8;
                    word = x1 >> shift;
                    if word > 47 then
                        if 58 > word then
                            foundNum = 1;
                            digit = word - 48
                        end
                    end;
                    if foundNum > 0 then
                        num = num * mult;
                        num = num + digit;
                        shift = x2 - wordLen;
                        shift = shift * 8;
                        word = word << shift;
                        x2 = x2 - wordLen;
                        x1 = x1 - word
                    end
                end;
                lol = 0
            end;
            x0 = num
        """
        args1 = {"n1": 0}

        expected_result1 = 3245

        results = compile_and_run(code, "test_self_compiler_lexer_bug", [args1])
        
        result1 = results[0]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")

    def test_find_prim(self):
        code = """
            /*

            Ein Programm, um die nte Primzahl zu finden.

            Input:
            - n1: Die Nummer der Primzahl, die gefunden werden soll.

            */

            let n, zahl, teiler, istPrim, res;
            n = x1; // Obergrenze
            zahl = 2;  // Startwert

            while n > zahl - 1 do
                teiler = 2;
                istPrim = 1;

                while zahl > teiler * teiler do
                    if zahl % teiler == 0 then
                        istPrim = 0
                    end;
                    teiler = teiler + 1
                end;

                if istPrim == 1 then
                    res = zahl
                end;
                
                zahl = zahl + 1
            end;

            x0 = res
        """
        args1 = {"n1": 100}
        args4 = {"n1": 0}

        expected_result1 = 97
        expected_result2 = 0

        results = compile_and_run(code, "test_find_prim", [args1, args4])
        
        result1 = results[0]
        result2 = results[1]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args4} failed, expected {expected_result2}, got {result2}")

    def test_unary_lists(self):
        code = """
            /*

            Simple EWHILE Program to demonstrate unary lists.

            */


            let list, shift, add, addAnother;
            shift = 1;

            add = x1;
            list = list << shift;
                list = list + 1;
                while add > 0 do
                    list = list << shift;
                    add = add - 1
                end;

            add = x2;
            list = list << shift;
                list = list + 1;
                while add > 0 do
                    list = list << shift;
                    add = add - 1
                end;


            if list == 3 then
                x0 = 0 // empty list
            else
                x0 = list
            end
        """
        args1 = {"n1": 100}
        args4 = {"n1": 0}
        args3 = {"n1": 1}

        # TODO: Add n2 value case

        expected_result1 = 2535301200456458802993406410753
        expected_result2 = 0
        expected_result3 = 5

        results = compile_and_run(code, "test_unary_lists", [args1, args4, args3])
        
        result1 = results[0]
        result2 = results[1]
        result3 = results[2]

        self.assertEqual(result1, expected_result1, f"Test case with {args1} failed, expected {expected_result1}, got {result1}")
        self.assertEqual(result2, expected_result2, f"Test case with {args4} failed, expected {expected_result2}, got {result2}")
        self.assertEqual(result3, expected_result3, f"Test case with {args3} failed, expected {expected_result3}, got {result3}")