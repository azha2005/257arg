<#
 Mediciones sobre el PNG de referencia (1999.png) para calibrar una composicion.
   .\measure_png.ps1 -Png 1999.png -Cmd frames               # lineas largas del color de los marcos (#616261): rectangulos de los insets
   .\measure_png.ps1 -Png 1999.png -Cmd bbox -R 220 -G 1 -B 67 -Tol 8 -X0 30 -Y0 200 -X1 340 -Y1 530   # caja de un color en una region
   .\measure_png.ps1 -Png 1999.png -Cmd px -X0 300 -Y0 1350                                          # color de un pixel
#>
param([string]$Png,[string]$Cmd,[int]$R=0,[int]$G=0,[int]$B=0,[int]$Tol=8,[int]$X0=0,[int]$Y0=0,[int]$X1=0,[int]$Y1=0,[int]$Min=60)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @'
using System; using System.Drawing; using System.Drawing.Imaging; using System.Text;
public static class PM {
  static int W,H; static byte[] D;
  public static void Load(string p){ var b=new Bitmap(p); W=b.Width;H=b.Height; var bd=b.LockBits(new Rectangle(0,0,W,H),ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb); D=new byte[bd.Stride*H]; System.Runtime.InteropServices.Marshal.Copy(bd.Scan0,D,0,D.Length); b.UnlockBits(bd); b.Dispose(); }
  static bool Frame(int x,int y){int i=(y*W+x)*4; return D[i+3]>120 && Math.Abs(D[i+2]-97)<14&&Math.Abs(D[i+1]-98)<14&&Math.Abs(D[i]-97)<14;}
  public static string Frames(int minLen){var sb=new StringBuilder();
    for(int y=0;y<H;y++){int s=-1; for(int x=0;x<=W;x++){bool f=x<W&&Frame(x,y); if(f&&s<0)s=x; if(!f&&s>=0){ if(x-s>=minLen)sb.AppendLine("H y="+y+" x="+s+".."+(x-1)); s=-1;}}}
    for(int x=0;x<W;x++){int s=-1; for(int y=0;y<=H;y++){bool f=y<H&&Frame(x,y); if(f&&s<0)s=y; if(!f&&s>=0){ if(y-s>=minLen)sb.AppendLine("V x="+x+" y="+s+".."+(y-1)); s=-1;}}}
    return sb.ToString();}
  public static string BBox(int r,int g,int b,int tol,int x0,int y0,int x1,int y1){int minx=99999,miny=99999,maxx=-1,maxy=-1;
    for(int y=y0;y<y1;y++)for(int x=x0;x<x1;x++){int i=(y*W+x)*4; if(D[i+3]<200)continue; if(Math.Abs(D[i+2]-r)<=tol&&Math.Abs(D[i+1]-g)<=tol&&Math.Abs(D[i]-b)<=tol){if(x<minx)minx=x;if(x>maxx)maxx=x;if(y<miny)miny=y;if(y>maxy)maxy=y;}}
    return minx+","+miny+" - "+maxx+","+maxy;}
  public static string Px(int x,int y){int i=(y*W+x)*4; return string.Format("#{0:x2}{1:x2}{2:x2} a={3}",D[i+2],D[i+1],D[i],D[i+3]);}
}
'@ -ReferencedAssemblies System.Drawing
[PM]::Load($Png)
switch ($Cmd) { "frames" { [PM]::Frames($Min) } "bbox" { [PM]::BBox($R,$G,$B,$Tol,$X0,$Y0,$X1,$Y1) } "px" { [PM]::Px($X0,$Y0) } }
