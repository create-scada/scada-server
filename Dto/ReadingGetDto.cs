using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Scada.Dto;

public class ReadingGetDto
{
    public int Id { get; set; }
    public string RtuAddress { get; set; }
    public string DeviceAddress { get; set; }
    public DateTime Date { get; set; }
    public string Schema { get; set; }
    public string PointData { get; set; }
}