import rpyc
import ast
import os
import sys
import difflib

from rpyc.utils.server import ThreadedServer

PORT = 18861
FILE_PATH = 'Received_codes'	# folder, w ktorym skladowane sa zapamietanie kody przeslane przez uzytkownikow
DIRECTORY = None			# sciezka do pliku z zapisanymi kodami
TMP_FILE = 'tmp.txt'	# plik tymaczsowy, uzywany do zapisania wyniku dzialania skryptu

#Czesc Tomek

#Czesc Tomek end
	
	# Odpowiada za wykonanie odebranego kodu po stronie serwera. Zapisuje jego wynik do pliku tymczasowego, 
	# skad jest ona przesylana spowrotem do klienta, po czym plik jest usuwany
	def exposed_execute_code(self):
		result = ''
		exec(self.code)
		with open(TMP_FILE, 'r') as tmp_file:
			result = tmp_file.read()
		os.remove(TMP_FILE)
		return result
	pass
	
	# Przechowuje kody przyslane przez klientow. Format zapisanego pliku: conn{x}, gdzie x to numer polaczenia. 
	# Dodatkowo sprawdza, czy plik o podanej nazwie juz istnieje
	def store_code(self):
		file_name = self._conn._config["connid"] + '.txt'
		file_localization = os.path.join(DIRECTORY, file_name)
		if not os.path.exists(file_localization):
			with open(file_localization, 'w') as text_file:
				text_file.write(self.code)
		print('Succesfully saved the code!')
		self.code = None
	pass
	
	# Odpowiada za porownanie otrzymanego kodu, z pozostalymi otrzymanymi podczas trwania sesji. 
	# Porownuje skladnie tych plikow, i zwraca czy oraz ktore z nich roznia sie (badz nie) pod wzgledem skladni. Jesli sie roznia, klient otrzymuje pelen wydruk(podobny jak diff z gita)
	def exposed_compare_codes(self):
		result = ''
		d = difflib.Differ()
		if os.listdir(DIRECTORY):
			for file in os.listdir(DIRECTORY):
				with open(os.path.join(DIRECTORY, file), 'r') as content_file:
					content = content_file.read()
					if content == self.code:
						result += 'Code same as in {}\n'.format(file)
					else:
						result += 'Differences with {}'.format(file)
						diff = d.compare(self.code.splitlines(), content.splitlines())
						result += '\n'.join(list(diff))
		self.store_code()
		return result
	pass
	
if __name__ == "__main__":
	
	DIRECTORY = os.path.join(os.getcwd(), FILE_PATH) # lokalizacja, w ktorej bedziemy zapisywac otrzymane od klientow kody
	if not os.path.exists(DIRECTORY): # jesli folder nie istnieje, utworz go
		os.makedirs(FILE_PATH)
	elif os.listdir(DIRECTORY): # jesli cos istnieje w folderze
		filelist = [ f for f in os.listdir(DIRECTORY) ]
		for f in filelist:		# usun cala zawartosc
			os.remove(os.path.join(DIRECTORY, f))
	
	thread = ThreadedServer(MyService, port = PORT)
	thread.start()