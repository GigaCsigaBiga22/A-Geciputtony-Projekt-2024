import platform
import psutil
import GPUtil
import cpuinfo
import math
from pySMART import Device
from pySMART import DeviceList
from pySMART import Attribute
from pySMART import SMARTCTL
import wmi
import win32api
import win32com
import win32com.client
import tkinter as tk
import os
import subprocess

SMARTCTL.sudo = True
w = wmi.WMI()

#Figyelmeztetés
print("="*22, "Figyelmeztetés! A program csakis kizárólag Windows rendszereken működik.", "="*23, "\n\n")

# Rendszerinformáció begyűjtése
system_info = platform.uname()
print("="*5, "Rendszerinfó:", "="*5)
print(f"--> Operációs rendszer: {system_info.system} {system_info.release} - {system_info.version}")
print(f"--> Gép neve: {system_info.node}\n")

# Processzorinformációk begyűjtése
cpu_info = cpuinfo.get_cpu_info()
physical_cores = psutil.cpu_count(logical=False)
print("="*5, "Processzorinformációk:", "="*5)
print(f"--> {cpu_info['brand_raw']}")
print(f"--> Architektúra: {cpu_info['arch']} ({cpu_info['bits']} bit-es processzor)")
print(f"--> Magok és LP-k száma: {physical_cores} mag és {cpu_info['count']} logikai processzor található")
hz_advertised_friendly = cpu_info['hz_advertised_friendly'].replace(' GHz', '')
print(f"--> Órajel: {round(float(hz_advertised_friendly), 1)} GHz\n")

# Memória-információk begyűjtése
ram_info = psutil.virtual_memory()
mems = w.Win32_PhysicalMemory()
print("="*5, "Memóriával kapcsolatos információk:", "="*5)
print(f"--> Összes telepített mennyiség: {round(ram_info.total / (1024.0 **3)):.0f} GB")

# foglalt és szabad bővítőhelyek lekérése
for bovitohely in w.Win32_PhysicalMemoryArray():
    try:
        elerhetoBovHelyek = bovitohely.MemoryDevices
        foglaltBovHelyek = len(list(w.Win32_PhysicalMemory()))
        print(f"--> Használt bővítőhelyek (slotok): {foglaltBovHelyek} / {elerhetoBovHelyek}\n")
    except AttributeError as objektumTulajdonságiHiba:
        print(f"    Hiba a Mátrixban.\n"
              f"    Hibakód: {str(objektumTulajdonságiHiba)}")

for mem in w.Win32_PhysicalMemory():
    try:
        # kártyagyártó vállalat neve:
        print(f"--> (RAM)Kártya gyártója: {mem.Manufacturer}")
        # kártya modellszáma:
        print(f"    Kártya modellje: {str(mem.PartNumber)}")
        # kártya sorozatszáma:
        print(f"    Kártya sorozatszáma: {str(mem.SerialNumber)}")
        # kártya kapacitása GB-ban, kerekítéssel):
        print(f"    Kártya mérete/kapacitása: {round(int(mem.Capacity) / (1024**3))} GB")
        # kártya sebessége Megaertzben:
        print(f"    Kártya sebessége: {int(mem.Speed)} MHz")
        #DDR-generáció meghatározása:
        smBIOS_mem_tipus = int(mem.SMBIOSMemoryType)
        if smBIOS_mem_tipus == 27:
            print("    Memória típusa: DDR5")
        elif smBIOS_mem_tipus == 26:
            print("    Memória típusa: DDR4")
        elif smBIOS_mem_tipus == 24:
            print("    Memória típusa: DDR3")
        elif smBIOS_mem_tipus == 21:
            print("    Memória típusa: DDR2")
        elif smBIOS_mem_tipus == 20:
            print("    Memória típusa: DDR")
        else:
            print(f"    Hiba. Memória típusa ismeretlen (kódja: {str(smBIOS_mem_tipus)}.\n "
                  f"    Azért láthatod ezt a hibaüzenetet, mert\n "
                  f"    1.) - A vizsgált memória DDR6-os, vagy\n "
                  f"    2.) - Nem DDR-típusú memória van a számítógépben, vagy\n "
                  f"    3.) - A RAM kártya nem tartalmaz ilyen információt, de ha mégis, esetleg sérülten tartalmazza, vagy\n "
                  f"    4.) - A Windows valamiért nem tudja beolvasni ezt az adatot.")

        # Foglalat/kártyatípus meghatározása:
        ramFoglalat = int(mem.FormFactor)
        if ramFoglalat == 8:
            print("    Foglalat típusa: DIMM (Dual Inline Memory Module)\n")
        elif ramFoglalat == 12:
            print("    Foglalat típusa: SO-DIMM (Small Outline Dual Inline Memory Module)\n")
        elif ramFoglalat == 16:
            print("    Foglalat típusa: LRDIMM (Load-Reduced DIMM)\n")
        elif ramFoglalat == 1:
            print("    Foglalat típusa: UDIMM (Unbuffered DIMM)\n")
        elif ramFoglalat == 2:
            print("    Foglalat típusa: FBDIMM (Fully Buffered DIMM) [FÉSZBÚK DIMM, hehe]\n")
        elif ramFoglalat == 5:
            print("    Foglalat típusa: Mini-DIMM (Mini Dual Inline Memory Module)\n")
        else:
            print("    Ácsi. Ötletem sem volt, hogy ilyen RAM-foglalat létezik.\n"
                  f"    (Hiba. Ismeretlen foglalat. Kódja: {str(ramFoglalat)})\n")

    except AttributeError as objektumTulajdonságiHiba:
        print(f"    Hiba. Néhány alkatrész információ lekérdezése sikertelennek bizonyult.\n"
              f"    Hibakód:\n{str(objektumTulajdonságiHiba)}\n")

# Videóvezérlővel kapcsolatos információk begyűjtése
gpus = GPUtil.getGPUs()
if gpus:
    print("="*5, "Videóvezérlővel kapcsolatos információk", "="*5)
    for gpu in gpus:
        print(f"--> Megnevezés: {gpu.name}")
        print(f"--> Összes található videómemóra: {round(gpu.memoryTotal)} MB\n")
else:
    print("----> Megjegyzés: Nem található videóvezérlő.\n")

#def hatT_info_gyujtes(hatT_utv): # Háttértár(ak)kal kapcsolatos információk begyűjtése
try:
    print("="*5, "Háttértár(ak)kal kapcsolatos információk:", "="*5)
    hattertarLista = DeviceList()
    for hattertar in hattertarLista.devices:
        eppenVizsgaltHattertar = hattertar
        print(f"--> Háttértár gyártója: {eppenVizsgaltHattertar.vendor}")
        if str(eppenVizsgaltHattertar.family) == "None":
            print(f"--> Háttértár termékcsaládja: Nem sikerült lekérni.")
        else:
            print(f"--> Háttértár termékcsaládja: {eppenVizsgaltHattertar.family}")
        print(f"--> Háttértár modellje: {eppenVizsgaltHattertar.model}")
        print(f"--> Háttértár sorozatszáma: {eppenVizsgaltHattertar.serial}")
        if round((eppenVizsgaltHattertar.size) / math.pow(1024, 3)) <= 500:
            print(f"--> Háttértár mérete: {round((eppenVizsgaltHattertar.size) / math.pow(1024, 3))} GB")
        else:
            print(f"--> Háttértár mérete: {round((eppenVizsgaltHattertar.size) / math.pow(1024, 4))} TB")
        if eppenVizsgaltHattertar.rotation_rate is None:
            print(f"--> Háttértár típusa: {eppenVizsgaltHattertar._interface} csatlakozojú SSD\n")
        elif eppenVizsgaltHattertar.rotation_rate > 0:
            print(f"--> Háttértár típusa: {eppenVizsgaltHattertar._interface} csatlakozójú HDD vagy SSHD\n")
        else:
            print(f"--> Segítség, nemtommivan.\n--> (Annyi mindenképp, hogy a programnak nem sikerült megállapítania a háttértár típusát.)\n")
except Exception as hibaLeirasHATTERTAR:
    print(f"--> Hiba! Leírás: {hibaLeirasHATTERTAR}\n")


# Kijelzővel kapcsolatos információk begyüjtése: #ez egy rakat szar, 4db Tkinter ablakot nyit fel, amikón nekem 1 se kéne xd (tudommér, csak szopás, na)
print("="*5, "Kijelzővel kapcsolatos információk:", "="*5)


# Get keyboard and mouse information

#input("Nyomj Enter-t a kilépéshez...")