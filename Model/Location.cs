namespace Scada.Models;

public class Location
{
    public int Id { get; set; }
    public string Name { get; set; }
    public string ImageData { get; set; }
    public List<Device> Devices { get; set; }
}