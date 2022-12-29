namespace Scada.Dto;

public class DevicePostDto
{
    public string RtuAddress { get; set; }
    public string DeviceAddress { get; set; }
    public string Schema { get; set; }
    public double X { get; set; }
    public double Y { get; set; }
    public string ImagePath { get; set; }
    public List<DisplayPointPostDto> DisplayPoints { get; set; }
    public int LocationId { get; set; }
}