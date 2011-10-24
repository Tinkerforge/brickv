Name "Brickv Windows Installer"

OutFile "brickv_windows.exe"

; The default installation directory
InstallDir $PROGRAMFILES\Tinkerforge\Brickv

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "SOFTWARE\TINKERFORGE\BRICKV" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------

!define BRICKV_VERSION "1.0.0"

;--------------------------------

!macro macrouninstall

  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Brickv"
  DeleteRegKey HKLM SOFTWARE\TINKERFORGE\BRICKV


  ; Remove directories used
  RMDir /R $INSTDIR\OpenGL
  RMDir /R $INSTDIR\OpenGL_accelerate
  RMDir /R $INSTDIR\tcl
  RMDir /R $INSTDIR\libs
  RMDir /R $INSTDIR\mpl-data
  RMDir /R $INSTDIR\plugin_system  
  RMDir /R "$INSTDIR"
  ;Delete $INSTDIR\*
  
  ; Remove menu shortcuts
  ;Delete "$SMPROGRAMS\Tinkerforge\Brickv.lnk"
  RMDir /R "$SMPROGRAMS\Tinkerforge"
  
!macroend


; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

!include "WordFunc.nsh"
  !insertmacro VersionCompare



; The stuff to install
Section "Install Brickv Programm"

; Check to see if already installed
  ClearErrors
  ReadRegStr $0 HKLM SOFTWARE\TINKERFORGE\BRICKV "Version"
  IfErrors install ;Version not set, install
  ${VersionCompare} $0 ${BRICKV_VERSION} $1
  IntCmp $1 2 uninstall
    MessageBox MB_YESNO|MB_ICONQUESTION "Brickv version $0 seems to be already installed on your system.$\n\
    Would you like to proceed with the installation of version ${BRICKV_VERSION}?$\n\
    Old Version will be first uninstalled." \
        IDYES uninstall IDNO quit

  quit:
     Quit

  uninstall:
     !insertmacro macrouninstall

  install:
  
  SetOutPath $INSTDIR
  File "..\*"
  
  SetOutPath $INSTDIR\OpenGL
  File /r "..\OpenGL\*"
  
  SetOutPath $INSTDIR\OpenGL_accelerate
  File /r "..\OpenGL_accelerate\*"
  
  SetOutPath $INSTDIR\tcl
  File /r "..\tcl\*"
  
  SetOutPath $INSTDIR\libs
  File /r "..\libs\*"
  
  SetOutPath $INSTDIR\mpl-data
  File /r "..\mpl-data\*"
  
  SetOutPath $INSTDIR\plugin_system
  File /r "..\plugin_system\*"
  
  

  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\TINKERFORGE\BRICKV "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM SOFTWARE\TINKERFORGE\BRICKV "Version" ${BRICKV_VERSION}
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Brickv" "DisplayName" "Brickv"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Brickv" "Publisher" "Tinkerforge GmbH"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Brickv" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Brickv" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Brickv" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
  ; Create start menu shortcut
  SetOutPath $INSTDIR\	; set working directory for main.exe
  createDirectory "$SMPROGRAMS\Tinkerforge"
  createShortCut "$SMPROGRAMS\Tinkerforge\Brickv.lnk" "$INSTDIR\main.exe"

SectionEnd
;--------------------------------

; Uninstaller

Section "Uninstall"

  !insertmacro macrouninstall

SectionEnd
