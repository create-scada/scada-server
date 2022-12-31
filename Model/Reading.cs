using System.ComponentModel.DataAnnotations.Schema;
using Newtonsoft.Json.Linq;

namespace Scada.Models;

public class Reading
{
    public int Id { get; set; }
    public string RtuAddress { get; set; }
    public string DeviceAddress { get; set; }
    public DateTime Date { get; set; }
    public string Schema { get; set; }
    [Column(TypeName = "jsonb")]
    public JObject PointData { get; set; }
}