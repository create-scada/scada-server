using Newtonsoft.Json.Linq;


namespace Scada.Dto;

public class ReadingPostDto
{
    public string RtuAddress { get; set; }
    public string DeviceAddress { get; set; }
    public DateTime Date { get; set; }
    public string Schema { get; set; }
    public JObject PointData { get; set; }
}