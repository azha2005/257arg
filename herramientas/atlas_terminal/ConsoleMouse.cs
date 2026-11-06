// Adaptador para conhost: observa clics sin consumir las teclas que lee Node.
// Windows Terminal y las demás terminales usan los eventos SGR del visor.
using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;

public static class AtlasConsoleMouse
{
    [StructLayout(LayoutKind.Sequential)] struct Point { public int X, Y; }
    [StructLayout(LayoutKind.Sequential)] struct Coord { public short X, Y; }
    [StructLayout(LayoutKind.Sequential)] struct Rect { public short Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] struct BufferInfo
    {
        public Coord Size, Cursor;
        public ushort Attributes;
        public Rect Window;
        public Coord Maximum;
    }
    [StructLayout(LayoutKind.Sequential)] struct FontInfo
    {
        public uint Index;
        public Coord Size;
    }
    [DllImport("kernel32.dll")] static extern IntPtr GetConsoleWindow();
    [DllImport("kernel32.dll")] static extern bool AttachConsole(uint processId);
    [DllImport("kernel32.dll")] static extern bool FreeConsole();
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern Microsoft.Win32.SafeHandles.SafeFileHandle CreateFile(string path, uint access, uint share, IntPtr security, uint creation, uint flags, IntPtr template);
    [DllImport("kernel32.dll")] static extern bool GetConsoleScreenBufferInfo(IntPtr output, out BufferInfo info);
    [DllImport("kernel32.dll")] static extern bool GetCurrentConsoleFont(IntPtr output, bool maximum, out FontInfo info);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr window);
    [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] static extern IntPtr WindowFromPoint(Point point);
    [DllImport("user32.dll")] static extern IntPtr GetAncestor(IntPtr window, uint flag);
    [DllImport("user32.dll")] static extern bool GetCursorPos(out Point point);
    [DllImport("user32.dll")] static extern bool ScreenToClient(IntPtr window, ref Point point);
    [DllImport("user32.dll")] static extern short GetAsyncKeyState(int key);
    [DllImport("user32.dll")] static extern bool SetProcessDPIAware();

    public static void Run(int parentId)
    {
        // Guardar el pipe antes de adjuntarse: AttachConsole puede cambiar stdout.
        using (var writer = new System.IO.StreamWriter(Console.OpenStandardOutput(), new System.Text.UTF8Encoding(false)))
        {
        writer.AutoFlush = true;
        IntPtr window = GetConsoleWindow();
        if (window == IntPtr.Zero || !IsWindowVisible(window))
        {
            FreeConsole();
            if (!AttachConsole((uint)parentId)) return;
            window = GetConsoleWindow();
        }
        // El stdout del adaptador es un pipe; abrir el buffer visible del padre.
        if (window == IntPtr.Zero || !IsWindowVisible(window)) return;
        using (var consoleOutput = CreateFile("CONOUT$", 0xC0000000, 3, IntPtr.Zero, 3, 0, IntPtr.Zero))
        using (Process parent = Process.GetProcessById(parentId))
        {
            if (consoleOutput.IsInvalid) return;
            IntPtr output = consoleOutput.DangerousGetHandle();
            SetProcessDPIAware();
            writer.WriteLine("ready");
            bool pressed = false;
            short lastWidth = 0, lastHeight = 0;
            int ticks = 0;
            while (!parent.HasExited)
            {
                if (ticks++ % 20 == 0)
                {
                    FontInfo measured;
                    if (GetCurrentConsoleFont(output, false, out measured) && measured.Size.X > 0 && measured.Size.Y > 0 &&
                        (measured.Size.X != lastWidth || measured.Size.Y != lastHeight))
                    {
                        lastWidth = measured.Size.X; lastHeight = measured.Size.Y;
                        writer.WriteLine("font;" + lastWidth + ";" + lastHeight);
                    }
                }
                bool down = (GetAsyncKeyState(1) & 0x8000) != 0;
                if (down && !pressed && GetForegroundWindow() == window)
                {
                    Point point;
                    BufferInfo buffer;
                    FontInfo font;
                    if (GetCursorPos(out point) && GetAncestor(WindowFromPoint(point), 2) == window &&
                        ScreenToClient(window, ref point) && GetConsoleScreenBufferInfo(output, out buffer) &&
                        GetCurrentConsoleFont(output, false, out font) && font.Size.X > 0 && font.Size.Y > 0 && point.X >= 0 && point.Y >= 0)
                    {
                        int x = point.X / font.Size.X, y = point.Y / font.Size.Y;
                        if (x <= buffer.Window.Right - buffer.Window.Left && y <= buffer.Window.Bottom - buffer.Window.Top)
                        {
                            writer.WriteLine((x + 1) + ";" + (y + 1));
                        }
                    }
                }
                pressed = down;
                Thread.Sleep(15);
            }
        }
        }
    }
}
