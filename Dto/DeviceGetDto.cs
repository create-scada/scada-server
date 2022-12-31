namespace Scada.Dto;

using Newtonsoft.Json.Linq;

public class DeviceGetDto
{
    public int Id { get; set; }
    public string RtuAddress { get; set; }
    public string DeviceAddress { get; set; }
    public string Schema { get; set; }
    public JObject PointData { get; set; }
    public double X { get; set; }
    public double Y { get; set; }
    public string ImagePath { get; set; }
    public List<DisplayPointGetDto> DisplayPoints { get; set; }
    public int LocationId { get; set; }
}