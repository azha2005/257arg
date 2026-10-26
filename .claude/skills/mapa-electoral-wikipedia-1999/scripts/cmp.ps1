<#
 Compara una captura propia (1920x1649) con el PNG de referencia.
   -Cmd pair  : guarda referencia (sobre blanco) | mia, lado a lado, de la region X,Y,W,H con zoom S
   -Cmd shift : mejor desplazamiento (dx,dy) que hay que aplicar a la mia para que sus lineas blancas coincidan
                con las de la referencia en esa region (usar bloques con muchas lineas internas; en bloques
                que son casi todo fondo el resultado no sirve). La captura propia tiene que tener fondo NEGRO.
 Uso:  .\cmp.ps1 -Ref 1999.png -Cmd pair -Mine mine.png -Out par.png -X 320 -Y 270 -W 340 -H 440 -S 2
#>
param([string]$Cmd,[string]$Mine,[string]$Ref,[string]$Out="",[int]$X=0,[int]$Y=0,[int]$W=100,[int]$H=100,[int]$S=2,[int]$R=5)
Add-Type -AssemblyName System.Drawing
if (-not ([System.Management.Automation.PSTypeName]'CMP2').Type) {
Add-Type -TypeDefinition @"
using System; using System.Drawing; using System.Drawing.Imaging; using System.Text;
public static class CMP2 {
  static byte[] LoadMask(string p,bool onWhite,out int W,out int H){
    var b=new Bitmap(p); W=b.Width;H=b.Height; var bd=b.LockBits(new Rectangle(0,0,W,H),ImageLockMode.ReadOnly,PixelFormat.Format32bppArgb);
    var D=new byte[bd.Stride*H]; System.Runtime.InteropServices.Marshal.Copy(bd.Scan0,D,0,D.Length); b.UnlockBits(bd); b.Dispose();
    var m=new byte[W*H];
    for(int i=0;i<W*H;i++){ int a=D[i*4+3]; int r=D[i*4+2],g=D[i*4+1],bl=D[i*4];
      m[i]=(byte)((a>200&&r>228&&g>228&&bl>228)?1:0); }
    return m; }
  public static string Block(string refp,string minep,int x,int y,int w,int h,int R){
    int W,H,W2,H2; var a=LoadMask(refp,true,out W,out H); var b=LoadMask(minep,false,out W2,out H2);
    int best=-1,bdx=0,bdy=0;
    for(int dy=-R;dy<=R;dy++)for(int dx=-R;dx<=R;dx++){ int sc=0;
      for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++){ if(a[j*W+i]==1&&b[(j+dy)*W2+(i+dx)]==1)sc++; }
      if(sc>best){best=sc;bdx=dx;bdy=dy;} }
    int na=0,nb=0; for(int j=y;j<y+h;j++)for(int i=x;i<x+w;i++){ if(a[j*W+i]==1)na++; if(b[j*W2+i]==1)nb++; }
    return "block("+x+","+y+","+w+","+h+") mine needs dx="+(-bdx)+" dy="+(-bdy)+"  overlap="+best+" ref-white="+na+" mine-white="+nb; }
  public static void Pair(string refp,string minep,string outp,int x,int y,int w,int h,int scale){
    var r=new Bitmap(refp); var m=new Bitmap(minep);
    var o=new Bitmap(w*scale*2+10,h*scale); var g=Graphics.FromImage(o); g.Clear(Color.White);
    g.InterpolationMode=System.Drawing.Drawing2D.InterpolationMode.HighQualityBicubic;
    var rw=new Bitmap(r.Width,r.Height); var g2=Graphics.FromImage(rw); g2.Clear(Color.White); g2.DrawImage(r,0,0,r.Width,r.Height); g2.Dispose();
    g.DrawImage(rw,new Rectangle(0,0,w*scale,h*scale),x,y,w,h,GraphicsUnit.Pixel);
    g.DrawImage(m,new Rectangle(w*scale+10,0,w*scale,h*scale),x,y,w,h,GraphicsUnit.Pixel);
    o.Save(outp); g.Dispose(); o.Dispose(); r.Dispose(); m.Dispose(); rw.Dispose(); }
}
"@ -ReferencedAssemblies System.Drawing
}
$ref=$Ref
if ($Cmd -eq "pair") { [CMP2]::Pair($ref,$Mine,$Out,$X,$Y,$W,$H,$S); "saved $Out" }
elseif ($Cmd -eq "shift") { [CMP2]::Block($ref,$Mine,$X,$Y,$W,$H,$R) }
