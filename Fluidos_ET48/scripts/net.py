# Definición de la red (longitudes medidas sobre el DWG HOTEL_Trabajo_2026-27, cotas en m)
# fila: (ID, descripción, circuito AF/ACS, serie MC/PE/VAL, n_std, n_adp, n_ofi, Qt_extra(formula o num), Qmax_aparato, v_obj, L, K)
NDIR=globals().get('NDIR',5)
SOL=lambda k: 4.40+3.30*(k-1)   # solera planta k>=1
R=[]
def add(*a): R.append(a)
# ---------------- INSTALACIÓN GENERAL (AF + alimentación ACS)
QTOT="=Plantas!$S$17"   # Qt AF+ACS edificio
add('G1','Acometida: red general (fachada O) → hornacina contador','AF','PE',0,0,0,QTOT,0,1.2,14.0,0.6)
add('E1','Contador general (hornacina fachada O)','AF','VAL',0,0,0,QTOT,0,1.0,0,10)
add('E2','Válvula de retención general','AF','VAL',0,0,0,QTOT,0,1.0,0,2.5)
add('E3','Llaves de aislamiento contador (2 ud)','AF','VAL',0,0,0,QTOT,0,1.0,0,0.6)
add('G2','Tubo de alimentación: hornacina → cuarto AF sótano (colgado)','AF','PE',0,0,0,QTOT,0,1.2,14.0,0.3)
add('E4','Filtro general (cuarto AF)','AF','VAL',0,0,0,QTOT,0,1.0,0,5)
# ---------------- SUMINISTRO DIRECTO (PB-P5)
QDIR="=Plantas!$Q$5+Plantas!$Q$4"   # PB + sótano
add('D0','Colector directo (cuarto AF) + llave aislamiento','AF','MC',24*NDIR,2*NDIR,NDIR,"=Plantas!$Q$5+Plantas!$Q$4",0,1.0,2.0,0.3)
add('DL1','Directo: cuarto AF → base patinillo O','AF','MC',12*NDIR,2*NDIR,0,0,0,1.0,12.0,2.8)
add('DR1','Directo: cuarto AF → base patinillo E','AF','MC',12*NDIR,0,NDIR,0,0,1.0,48.0,2.8)
for k in range(1,NDIR+1):
    n=NDIR+1-k
    add(f'MDL{k}',f'Montante directo O: tramo hasta planta {k}','AF','MC',12*n,2*n,0,0,0,1.0,7.3 if k==1 else 3.3,0)
    add(f'MDR{k}',f'Montante directo E: tramo hasta planta {k}','AF','MC',12*n,0,n,0,0,1.0,7.3 if k==1 else 3.3,0)
# ---------------- BOMBEO (P6-P11) desde aljibe
add('BV0','Colector impulsión grupo (AF alta + alimentación ACS)','AF','MC',24*(11-NDIR),2*(11-NDIR),(11-NDIR),"=Plantas!$R$17",0,1.0,3.0,0.3)
add('BL1','Bombeo: cuarto AF → base patinillo O','AF','MC',12*(11-NDIR),2*(11-NDIR),0,0,0,1.0,12.0,2.8)
add('BR1','Bombeo: cuarto AF → base patinillo E','AF','MC',12*(11-NDIR),0,(11-NDIR),0,0,1.0,48.0,2.8)
for k in range(NDIR+1,12):
    n=12-k
    add(f'MBL{k}',f'Montante bombeo O: tramo hasta planta {k}','AF','MC',12*n,2*n,0,0,0,1.0,round(SOL(NDIR+1)+2.7+0.2,2) if k==NDIR+1 else 3.3,0)
    add(f'MBR{k}',f'Montante bombeo E: tramo hasta planta {k}','AF','MC',12*n,0,n,0,0,1.0,round(SOL(NDIR+1)+2.7+0.2,2) if k==NDIR+1 else 3.3,0)
# ---------------- RAMALES DE PLANTA TIPO (iguales en todas las plantas)
for c,s in (('AF',''),('ACS','C')):
    add(f'RL1{s}','Ramal planta O: patinillo → nudo hab. B1','%s'%c,'MC',12,2,0,0,0,1.0,3.9,0.3)
    add(f'RL2{s}','Ramal planta O: B1 → T1/B2','%s'%c,'MC',10,2,0,0,0,1.0,6.4,0)
    add(f'RL3{s}','Ramal planta O: T1/B2 → T2/B3','%s'%c,'MC',8,0,0,0,0,1.0,6.1,0)
    add(f'RL4{s}','Ramal planta O: T2/B3 → T3/B4','%s'%c,'MC',4,0,0,0,0,1.0,6.5,0)
    add(f'RL5{s}','Derivación a habitación más alejada O (T3/B4)','%s'%c,'MC',1,0,0,0,0,1.0,1.65,0.3)
    add(f'RR1{s}','Ramal planta E: patinillo → nudo hab. T7','%s'%c,'MC',12,0,1,0,0,1.0,1.0,0.3)
    add(f'RR2{s}','Ramal planta E: T7 → T6/B7','%s'%c,'MC',11,0,1,0,0,1.0,5.5,0)
    add(f'RR3{s}','Ramal planta E: T6/B7 → oficio','%s'%c,'MC',7,0,1,0,0,1.0,4.9,0)
    add(f'RR4{s}','Ramal planta E: oficio → T5/B6','%s'%c,'MC',7,0,0,0,0,1.0,1.6,0)
    add(f'RR5{s}','Ramal planta E: T5/B6 → T4/B5','%s'%c,'MC',4,0,0,0,0,1.0,6.5,0)
    add(f'RR6{s}','Derivación a habitación más alejada E (T4/B5)','%s'%c,'MC',1,0,0,0,0,1.0,1.65,0.3)
# ---------------- INTERIOR HABITACIÓN ESTÁNDAR (cuarto húmedo)
add('H1','Hab.: entrada → derivación bañera','AF','MC',1,0,0,0,0,0.6,0.6,0)
add('H2','Hab.: → derivación inodoro (lav+bidé+inod.)','AF','MC',0,0,0,"=Datos!$B$31+Datos!$B$34+Datos!$B$35",0,0.6,0.4,0)
add('H3','Hab.: → derivación bidé (lav+bidé)','AF','MC',0,0,0,"=Datos!$B$31+Datos!$B$34",0,0.6,0.6,0)
add('H4','Hab.: → lavabo (incl. bajada a +0,60)','AF','MC',0,0,0,"=Datos!$B$31","=Datos!$B$31",0.6,3.7,2)
add('H5','Hab.: derivación → bañera (incl. bajada)','AF','MC',0,0,0,"=Datos!$B$33","=Datos!$B$33",0.6,2.4,2)
add('HC1','Hab.: entrada → derivación bañera','ACS','MC',1,0,0,0,0,0.6,0.6,0)
add('HC2','Hab.: → derivación bidé (lav+bidé)','ACS','MC',0,0,0,"=Datos!$C$31+Datos!$C$34",0,0.6,1.0,0)
add('HC3','Hab.: → lavabo (incl. bajada a +0,60)','ACS','MC',0,0,0,"=Datos!$C$31","=Datos!$C$31",0.6,3.7,2)
add('HC4','Hab.: derivación → bañera (incl. bajada)','ACS','MC',0,0,0,"=Datos!$C$33","=Datos!$C$33",0.6,2.4,2)
# ---------------- PRODUCCIÓN Y DISTRIBUCIÓN ACS
add('BC1','Alimentación AF a producción ACS (grupo → cuarto ACS)','AF','MC',0,0,0,"=Plantas!$R$17",0,1.0,8.0,2.8)
add('E5','Acumuladores ACS (entrada + salida)','AF','VAL',0,0,0,"=Plantas!$R$17",0,1.0,0,3)
add('CAL1','ACS alta: cuarto ACS → base patinillo O','ACS','MC',12*(11-NDIR),2*(11-NDIR),0,0,0,1.0,20.7,0.3)
add('CAR1','ACS alta: cuarto ACS → base patinillo E','ACS','MC',12*(11-NDIR),0,(11-NDIR),0,0,1.0,39.0,0.3)
for k in range(NDIR+1,12):
    n=12-k
    add(f'MCAL{k}',f'Montante ACS alta O: tramo hasta planta {k}','ACS','MC',12*n,2*n,0,0,0,1.0,round(SOL(NDIR+1)+2.7+0.2,2) if k==NDIR+1 else 3.3,0)
    add(f'MCAR{k}',f'Montante ACS alta E: tramo hasta planta {k}','ACS','MC',12*n,0,n,0,0,1.0,round(SOL(NDIR+1)+2.7+0.2,2) if k==NDIR+1 else 3.3,0)
add('CB0','ACS baja: colector tras válvula reductora (PB-P'+str(NDIR)+')','ACS','MC',24*NDIR,2*NDIR,NDIR,"=Plantas!$R$5",0,1.0,2.0,0.3)
add('CBL1','ACS baja: cuarto ACS → base patinillo O','ACS','MC',12*NDIR,2*NDIR,0,0,0,1.0,20.7,0.3)
add('CBR1','ACS baja: cuarto ACS → base patinillo E','ACS','MC',12*NDIR,0,NDIR,0,0,1.0,39.0,0.3)
for k in range(1,NDIR+1):
    n=NDIR+1-k
    add(f'MCBL{k}',f'Montante ACS baja O: tramo hasta planta {k}','ACS','MC',12*n,2*n,0,0,0,1.0,7.3 if k==1 else 3.3,0)
    add(f'MCBR{k}',f'Montante ACS baja E: tramo hasta planta {k}','ACS','MC',12*n,0,n,0,0,1.0,7.3 if k==1 else 3.3,0)
# ---------------- PLANTA BAJA (ramal colgado del techo del sótano)
for c,s,Q in (('AF','','=Plantas!$Q$5'),('ACS','C','=Plantas!$R$5')):
    k=1 if c=='AF' else 2  # columna Locales
    col='L' if c=='AF' else 'M'
    add(f'PBW{s}','PB: cuarto → aseos públicos (O)',c,'MC',0,0,0,f'=Locales!${col}$7+Locales!${col}$8',0,1.0,12.0,0.3)
    add(f'PBE1{s}','PB: cuarto → barra',c,'MC',0,0,0,f'{Q}-Locales!${col}$7-Locales!${col}$8',0,1.0,4.0,0.3)
    add(f'PBE2{s}','PB: barra → vestuarios',c,'MC',0,0,0,f'{Q}-Locales!${col}$7-Locales!${col}$8-Locales!${col}$11',0,1.0,8.4,0)
    add(f'PBE3{s}','PB: vestuarios → cocina/c.frío/basuras',c,'MC',0,0,0,f'{Q}-Locales!${col}$7-Locales!${col}$8-Locales!${col}$11-Locales!${col}$9-Locales!${col}$10',0,1.0,9.0,0)
    add(f'PBE4{s}','PB: cocina → oficio PB',c,'MC',5,2,1,0,0,1.0,5.0,0)
    add(f'PBE5{s}','PB: oficio → habitaciones PB',c,'MC',5,2,0,0,0,1.0,5.5,0)
    add(f'PBE6{s}','PB: derivación hab. 002 (incl. subida forjado)',c,'MC',1,0,0,0,0,1.0,6.0,0.3)
# ---------------- RECORRIDOS
ROOM_AF_LAV=['H1','H2','H3','H4']; ROOM_AF_BAN=['H1','H5']
ROOM_C_LAV=['HC1','HC2','HC3']; ROOM_C_BAN=['HC1','HC4']
RL=['RL1','RL2','RL3','RL4','RL5']; RRr=['RR1','RR2','RR3','RR4','RR5','RR6']
RLc=[x+'C' for x in RL]; RRc=[x+'C' for x in RRr]
GEN=['G1','E1','E2','E3','G2','E4']
PATHS=[
 # (nombre, tipo, planta, z_solera, tramos)
 ('R1 AF directo O · P'+str(NDIR)+' · lavabo','DIR',NDIR,GEN+['D0','DL1']+[f'MDL{k}' for k in range(1,NDIR+1)]+RL+ROOM_AF_LAV),
 ('R2 AF directo O · P'+str(NDIR)+' · bañera','DIR',NDIR,GEN+['D0','DL1']+[f'MDL{k}' for k in range(1,NDIR+1)]+RL+ROOM_AF_BAN),
 ('R3 AF directo E · P'+str(NDIR)+' · lavabo','DIR',NDIR,GEN+['D0','DR1']+[f'MDR{k}' for k in range(1,NDIR+1)]+RRr+ROOM_AF_LAV),
 ('R4 AF directo E · P'+str(NDIR)+' · bañera','DIR',NDIR,GEN+['D0','DR1']+[f'MDR{k}' for k in range(1,NDIR+1)]+RRr+ROOM_AF_BAN),
 ('R5 AF bombeo O · P11 · lavabo','BOMB',11,['BV0','BL1']+[f'MBL{k}' for k in range(NDIR+1,12)]+RL+ROOM_AF_LAV),
 ('R6 AF bombeo O · P11 · bañera','BOMB',11,['BV0','BL1']+[f'MBL{k}' for k in range(NDIR+1,12)]+RL+ROOM_AF_BAN),
 ('R7 AF bombeo E · P11 · lavabo','BOMB',11,['BV0','BR1']+[f'MBR{k}' for k in range(NDIR+1,12)]+RRr+ROOM_AF_LAV),
 ('R8 AF bombeo E · P11 · bañera','BOMB',11,['BV0','BR1']+[f'MBR{k}' for k in range(NDIR+1,12)]+RRr+ROOM_AF_BAN),
 ('R9 ACS alta O · P11 · lavabo','BOMB',11,['BV0','BC1','E5','CAL1']+[f'MCAL{k}' for k in range(NDIR+1,12)]+RLc+ROOM_C_LAV),
 ('R10 ACS alta O · P11 · bañera','BOMB',11,['BV0','BC1','E5','CAL1']+[f'MCAL{k}' for k in range(NDIR+1,12)]+RLc+ROOM_C_BAN),
 ('R11 ACS alta E · P11 · lavabo','BOMB',11,['BV0','BC1','E5','CAR1']+[f'MCAR{k}' for k in range(NDIR+1,12)]+RRc+ROOM_C_LAV),
 ('R12 ACS alta E · P11 · bañera','BOMB',11,['BV0','BC1','E5','CAR1']+[f'MCAR{k}' for k in range(NDIR+1,12)]+RRc+ROOM_C_BAN),
 ('R13 ACS baja O · P'+str(NDIR)+' · lavabo','VRP',NDIR,['CB0','CBL1']+[f'MCBL{k}' for k in range(1,NDIR+1)]+RLc+ROOM_C_LAV),
 ('R14 ACS baja O · P'+str(NDIR)+' · bañera','VRP',NDIR,['CB0','CBL1']+[f'MCBL{k}' for k in range(1,NDIR+1)]+RLc+ROOM_C_BAN),
 ('R15 ACS baja E · P'+str(NDIR)+' · lavabo','VRP',NDIR,['CB0','CBR1']+[f'MCBR{k}' for k in range(1,NDIR+1)]+RRc+ROOM_C_LAV),
 ('R16 ACS baja E · P'+str(NDIR)+' · bañera','VRP',NDIR,['CB0','CBR1']+[f'MCBR{k}' for k in range(1,NDIR+1)]+RRc+ROOM_C_BAN),
 ('R17 AF directo PB · hab. 002 · lavabo','DIR',0,GEN+['D0','PBE1','PBE2','PBE3','PBE4','PBE5','PBE6']+ROOM_AF_LAV),
 ('R18 ACS baja PB · hab. 002 · lavabo','VRP',0,['CB0','PBE1C','PBE2C','PBE3C','PBE4C','PBE5C','PBE6C']+ROOM_C_LAV),
]
