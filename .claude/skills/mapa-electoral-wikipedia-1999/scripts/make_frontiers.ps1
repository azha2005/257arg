<#
 Extrae del PNG de referencia solo los pixeles grises (fronteras, rios limitrofes, contornos de Chile en Tierra del Fuego,
 nombres de paises vecinos, marcas de los zooms) y los guarda como PNG transparente: assets/frontiers.png.
 Ese arte es fijo (no depende de los datos). Las exclusiones tapan los insets, rotulos y la leyenda, que se dibujan aparte.
   .\make_frontiers.ps1 -Src 1999.png -Dst frontiers.png
 Si el PNG de referencia cambia de composicion, ajustar las exclusiones del bucle.
#>
param([string]$Src,[string]$Dst,[int]$X0=570,[int]$Y0=100,[int]$X1=1410,[int]$Y1=1640)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System; using System.Drawing; using System.Drawing.Imaging;
public static class FR { public static int Run(string src,string dst,int X0,int Y0,int X1,int Y1){
 var b=new Bitmap(src); int W=b.Width,H=b.Height; var bd=b.LockBits(new Rectangle(0,0,W,H),ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb);
 var D=new byte[bd.Stride*H]; System.Runtime.InteropServices.Marshal.Copy(bd.Scan0,D,0,D.Length); int st=bd.Stride; b.UnlockBits(bd); b.Dispose();
 int w=X1-X0,h=Y1-Y0; var o=new Bitmap(w,h,PixelFormat.Format32bppArgb); var od=o.LockBits(new Rectangle(0,0,w,h),ImageLockMode.WriteOnly,PixelFormat.Format32bppArgb);
 var O=new byte[od.Stride*h]; int kept=0;
 for(int y=Y0;y<Y1;y++)for(int x=X0;x<X1;x++){
  if(x<655&&y>=262&&y<=715) continue;               // insets Tucuman y Gran San Juan
  if(x>=1240&&y>=740) continue;                      // AMBA, Antartida, CABA
  if(x>=985&&x<=1185&&y>=1210&&y<=1510) continue;    // Exterior y Malvinas
  if(x>=1395&&y>=470) continue;                      // Resistencia
  int i=y*st+x*4; int bl=D[i],g=D[i+1],r=D[i+2],a=D[i+3]; if(a<8) continue;
  int mx=Math.Max(r,Math.Max(g,bl)),mn=Math.Min(r,Math.Min(g,bl)); if(mx-mn>18) continue;   // solo grises
  int lum=(r+g+bl)/3; if(lum>215) continue;                                                  // sin lineas blancas
  int j=(y-Y0)*od.Stride+(x-X0)*4; O[j]=(byte)bl;O[j+1]=(byte)g;O[j+2]=(byte)r;O[j+3]=(byte)a; kept++; }
 System.Runtime.InteropServices.Marshal.Copy(O,0,od.Scan0,O.Length); o.UnlockBits(od); o.Save(dst,ImageFormat.Png); o.Dispose(); return kept; } }
'@ -ReferencedAssemblies System.Drawing
"pixeles conservados: " + [FR]::Run($Src,$Dst,$X0,$Y0,$X1,$Y1)
