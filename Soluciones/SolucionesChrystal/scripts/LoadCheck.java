import net.sf.jasperreports.engine.JasperReport;
import net.sf.jasperreports.engine.util.JRLoader;
import java.io.File;

public class LoadCheck {
    public static void main(String[] args) throws Exception {
        File dir = new File(args[0]);
        File[] jasper = dir.listFiles(new java.io.FileFilter() {
            public boolean accept(File f) {
                return f.getName().toLowerCase().endsWith(".jasper");
            }
        });
        java.util.Arrays.sort(jasper);
        int ok = 0;
        for (File j : jasper) {
            try {
                JasperReport rep = (JasperReport) JRLoader.loadObject(j);
                System.out.println("OK   " + j.getName() + "  (nombre=" + rep.getName() + ")");
                ok++;
            } catch (Throwable t) {
                System.out.println("FAIL " + j.getName() + " -> " + t.getClass().getName() + ": " + t.getMessage());
            }
        }
        System.out.println("RESULTADO CARGA: " + ok + " de " + jasper.length + " .jasper cargables con JR 6.2.0");
    }
}