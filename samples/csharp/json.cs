using System.Text.Json.Serialization;
namespace csharptstoy;

/// <summary>
/// Represents the Tstoy file
/// </summary>
public class TstoyFile
{
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    [JsonPropertyName("updates")]
    public TstoyFileUpdates? Updates { get; set; }

}

/// <summary>
/// Represents the updates in a Tstoy file
/// </summary>
public class TstoyFileUpdates
{
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("automatic")]
    public bool Automatic { get; set; }
    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("checkFrequency")]
    public int CheckFrequency { get; set; }

    /// <summary>
    /// Checks if the TstoyFileUpdates object is not null.
    /// </summary>
    /// <param name="tstoyProperty">The TstoyFileUpdates object to check.</param>
    /// <returns>True if the object is not null, false otherwise.</returns>
    public static bool IsValueNotNull(TstoyFileUpdates tstoyProperty) => tstoyProperty != null;
}

/// <summary>
/// Represents the Tstoy configuration
/// </summary>
public class TstoyConfig
{
    [JsonPropertyName("ensure")]
    public string? Ensure { get; set; }

    [JsonPropertyName("scope")]
    public string? Scope { get; set; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("updateAutomatically")]
    public bool UpdateAutomatically { get; set; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingDefault)]
    [JsonPropertyName("updateFrequency")]
    public int UpdateFrequency{ get; set; }

}

