import idaapi
base = idaapi.get_imagebase()
addr = base + 0x149E
for i in range(14):
    idc.patch_byte(addr + i, 0x90)
print("[+] ExitProcess call NOPed")