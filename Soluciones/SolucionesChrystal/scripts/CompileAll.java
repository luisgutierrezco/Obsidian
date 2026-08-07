import net.sf.jasperreports.engine.JasperCompileManager;
import java.io.File;

public class CompileAll {
    public static void main(String[] args) throws Exception {
        File dir = new File(args[0]);
        File[] jrxmls = dir.listFiles(new java.io.FileFilter() {
            public boolean accept(File f) {
                return f.getName().toLowerCase().endsWith(".jrxml");
            }
        });
        if (jrxmls == null) {
            System.out.println("ERROR: no se puede leer el directorio " + dir);
            System.exit(2);
        }
        java.util.Arrays.sort(jrxmls);
        int ok = 0;
        for (File jr : jrxmls) {
            String jasperName = jr.getName().substring(0, jr.getName().length() - 6) + ".jasper";
            File jasper = new File(dir, jasperName);
            try {
                JasperCompileManager.compileReportToFile(jr.getAbsolutePath(), jasper.getAbsolutePath());
                System.out.println("OK   " + jr.getName());
                ok++;
            } catch (Throwable t) {
                System.out.println("FAIL " + jr.getName() + " -> " + t.getClass().getName() + ": " + t.getMessage());
            }
        }
        System.out.println("RESULTADO: " + ok + " de " + jrxmls.length + " compilados correctamente.");
    }
}