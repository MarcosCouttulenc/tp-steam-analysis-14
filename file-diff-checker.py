import difflib
from colorama import init, Fore

CANTIDAD_CLIENTES = 2

class FileDiffChecker:
    def __init__(self, file1, file2):
        self.file1 = file1
        self.file2 = file2
    
    def compare_files(self):
        with open(self.file1, 'r') as f1, open(self.file2, 'r') as f2:
            lines1 = f1.readlines()
            lines2 = f2.readlines()

        lines1_sorted = sorted(lines1)
        lines2_sorted = sorted(lines2)

        diffs = list(difflib.unified_diff(lines1_sorted, lines2_sorted, fromfile=self.file1, tofile=self.file2))
        
        if not diffs:  # Si no hay diferencias
            print(Fore.GREEN + "OK: Los archivos son idénticos.")
        else:
            print(Fore.RED + "Diferencias encontradas:")
            # Imprime las diferencias en rojo
            for line in diffs:
                print(Fore.RED + line, end='')

init(autoreset=True)

def main():
    validated_results = "resultados/resultados-buenos.txt"
    for i in range(CANTIDAD_CLIENTES):
        results_to_validate = f"resultados/resultados-{i}.txt"
        try:
            file_diff_checker = FileDiffChecker(validated_results, results_to_validate)
            file_diff_checker.compare_files()
        except:
            pass
        

main()
