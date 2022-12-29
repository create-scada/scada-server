using System.ComponentModel.DataAnnotations.Schema;

namespace Scada.Models;

public class Reading
{
    public int Id { get; set; }
    public string RtuAddress { get; set; }
    public string DeviceAddress { get; set; }
    public DateTime Date { get; set; }
    public string Schema { get; set; }
    [Column(TypeName = "jsonb")]
    public string PointData { get; set; }
}