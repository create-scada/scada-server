using System.ComponentModel.DataAnnotations.Schema;

namespace Scada.Models;

public class DisplayPoint
{
    public int Id { get; set; }
    public string Name { get; set; }
    public Device Device { get; set; }
    public int DeviceId { get; set; }
}