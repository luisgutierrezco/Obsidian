import net.sf.jasperreports.engine.JasperCompileManager;

public class CompileReports {
    public static void main(String[] args) throws Exception {
        String base = "C:\\ChrystalUltraPlus2022\\Reports1\\";
        String[] names = {
            "REP_FMT_INVENTORY_OPERATION_TRANSFER",
            "REP_FMT_INVENTORY_OPERATION_DETAILS_TRANSFER",
            "REP_FMT_INVENTORY_OPERATION_LOAD",
            "REP_FMT_INVENTORY_OPERATION_DETAILS_LOAD",
            "REP_FMT_INVENTORY_OPERATION_DOWNLOAD",
            "REP_FMT_INVENTORY_OPERATION_DETAILS_DOWNLOAD"
        };
        for (String n : names) {
            String jrxml = base + n + ".jrxml";
            String jasper = base + n + ".jasper";
            System.out.println("Compilando: " + n);
            JasperCompileManager.compileReportToFile(jrxml, jasper);
            System.out.println("  -> OK: " + jasper);
        }
        System.out.println("Listo!");
    }
}
