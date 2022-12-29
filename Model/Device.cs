using System.ComponentModel.DataAnnotations.Schema;

namespace Scada.Models;

public class Device
{
    public int Id { get; set; }
    public string RtuAddress { get; set; }
    public string DeviceAddress { get; set; }
    public string Schema { get; set; }
    [Column(TypeName = "jsonb")]
    public string PointData { get; set; }
    public double X { get; set; }
    public double Y { get; set; }
    public string ImagePath { get; set; }
    public int LocationId { get; set; }
    public Location Location { get; set; }
    public List<DisplayPoint> DisplayPoints { get; set; }
}